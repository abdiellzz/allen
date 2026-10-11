import {installErrorControls, showStartupError} from './error-ui.mjs';

installErrorControls();
// Keep the failure UI separate from the app's module graph so a missing course
// or dependency cannot leave a permanent loading message.
try { await import('./app.mjs'); }
catch { showStartupError(); }
