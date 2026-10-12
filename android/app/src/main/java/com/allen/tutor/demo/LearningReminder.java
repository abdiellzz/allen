package com.allen.tutor.demo;

import android.Manifest;
import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.BitmapFactory;
import android.os.Build;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/** Opt-in, on-device daily reminder. No exact-alarm permission, server, or worker. */
public final class LearningReminder extends BroadcastReceiver {
    static final String ACTION = "com.allen.tutor.demo.LEARNING_REMINDER";
    static final String CHANNEL = "allen_learning";
    static SharedPreferences preferences(Context context) {
        return context.getSharedPreferences("allen_reminders", Context.MODE_PRIVATE);
    }
    static boolean allowed(Context context) {
        if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) return false;
        NotificationManager manager = context.getSystemService(NotificationManager.class);
        NotificationChannel channel = manager.getNotificationChannel(CHANNEL);
        return manager.areNotificationsEnabled() && (channel == null || channel.getImportance() != NotificationManager.IMPORTANCE_NONE);
    }
    static void createChannel(Context context) {
        NotificationChannel channel = new NotificationChannel(CHANNEL, "Consejos de Allen", NotificationManager.IMPORTANCE_DEFAULT);
        channel.setDescription("Un recordatorio diario opcional para continuar tu aprendizaje");
        channel.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);
        context.getSystemService(NotificationManager.class).createNotificationChannel(channel);
    }
    private static PendingIntent alarmIntent(Context context) {
        return PendingIntent.getBroadcast(context, 31,
                new Intent(context, LearningReminder.class).setAction(ACTION),
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
    static void cancel(Context context) {
        context.getSystemService(AlarmManager.class).cancel(alarmIntent(context));
        context.getSystemService(NotificationManager.class).cancel(31);
    }
    static void schedule(Context context) {
        cancel(context);
        SharedPreferences prefs = preferences(context);
        if (!prefs.getBoolean("enabled", false) || !allowed(context)) return;
        Calendar next = Calendar.getInstance();
        next.set(Calendar.HOUR_OF_DAY, prefs.getInt("hour", 18));
        next.set(Calendar.MINUTE, prefs.getInt("minute", 0));
        next.set(Calendar.SECOND, 0);
        next.set(Calendar.MILLISECOND, 0);
        if (next.getTimeInMillis() <= System.currentTimeMillis()) next.add(Calendar.DAY_OF_YEAR, 1);
        context.getSystemService(AlarmManager.class).setAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP, next.getTimeInMillis(), alarmIntent(context));
    }
    @Override public void onReceive(Context context, Intent intent) {
        SharedPreferences prefs = preferences(context);
        if (!prefs.getBoolean("enabled", false)) return;
        if (!ACTION.equals(intent.getAction())) { schedule(context); return; }
        String today = new SimpleDateFormat("yyyy-MM-dd", Locale.ROOT).format(Calendar.getInstance().getTime());
        boolean send = allowed(context) && !MainActivity.foreground
                && !today.equals(prefs.getString("last_sent", ""));
        // Re-arm before posting; schedule() also clears the previous reminder notification.
        schedule(context);
        if (!send) return;
        String[] tips = {
            "¿Seguimos con un ejemplo? Cinco minutos pueden ser un buen comienzo.",
            "Tu actividad está guardada. Vuelve cuando quieras y avanzamos paso a paso.",
            "¿Qué recuerdas sin mirar? Podemos comprobarlo con una tarjeta de repaso.",
            "No necesitas hacerlo perfecto. Una pregunta y una pista pueden ayudarte a empezar.",
            "Hoy podemos aplicar una idea en una misión corta. Tú eliges el ritmo."
        };
        String text = tips[Calendar.getInstance().get(Calendar.DAY_OF_YEAR) % tips.length];
        String summary = prefs.getString("summary", "");
        if (summary.length() > 0) text = summary + " " + text;
        PendingIntent open = PendingIntent.getActivity(context, 32,
                new Intent(context, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP),
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification note = new Notification.Builder(context, CHANNEL)
                .setSmallIcon(R.drawable.ic_reminder)
                .setLargeIcon(BitmapFactory.decodeResource(context.getResources(), R.drawable.allen_logo_original))
                .setContentTitle("Allen te acompaña")
                .setContentText(tips[Calendar.getInstance().get(Calendar.DAY_OF_YEAR) % tips.length])
                .setStyle(new Notification.BigTextStyle().bigText(text))
                .setContentIntent(open).setAutoCancel(true)
                .setVisibility(Notification.VISIBILITY_PRIVATE)
                .setPublicVersion(new Notification.Builder(context, CHANNEL).setSmallIcon(R.drawable.ic_reminder)
                        .setContentTitle("ALLEN").setContentText("Tienes un recordatorio de aprendizaje").build())
                .build();
        if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) return;
        try {
            context.getSystemService(NotificationManager.class).notify(31, note);
            prefs.edit().putString("last_sent", today).apply();
        } catch (SecurityException ignored) { /* Permission can be revoked between check and delivery. */ }
    }
}
