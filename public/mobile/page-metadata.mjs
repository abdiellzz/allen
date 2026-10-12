export const pages = {
  profiles: ['Perfiles', 'Crea o elige un perfil local para aprender con ALLEN.'],
  today: ['Hoy', 'Continúa tu aprendizaje y revisa tu siguiente actividad recomendada.'],
  learn: ['Aprender', 'Explora materias, rutas y actividades para reforzar tus conocimientos.'],
  practice: ['Practicar', 'Practica con ejercicios, tarjetas, proyectos y el sendero de Allen.'],
  allen: ['Habla con Allen', 'Aclara dudas con explicaciones y preguntas preparadas del curso.'],
  progress: ['Mi progreso', 'Revisa tus objetivos comprobados, dificultades y próximos repasos.'],
  session: ['Mi actividad', 'Aprende paso a paso, pide pistas y comprueba tu comprensión.'],
  backup: ['Copia de progreso', 'Exporta y recupera una copia privada de tu progreso local.'],
  summary: ['Cierre de sesión', 'Descubre qué avanzaste y qué puedes reforzar después.'],
  settings: ['Ajustes', 'Configura la apariencia, accesibilidad y opciones de ALLEN.'],
  notebook: ['Cuaderno de descubrimientos', 'Guarda ideas y errores comprendidos por tema.'],
  game: ['El sendero de Allen', 'Explora tres senderos educativos a tu ritmo con Allen.'],
  error: ['No pudimos abrir ALLEN', 'Encuentra opciones para volver a abrir ALLEN sin borrar tu progreso.'],
};

export function setPageMetadata(view) {
  const [label, description] = pages[view] ?? pages.today;
  document.title = `${label} · ALLEN`;
  for (const [attribute, key, value] of [
    ['name', 'description', description], ['name', 'title', document.title],
    ['property', 'og:title', document.title], ['property', 'og:description', description],
    ['name', 'twitter:title', document.title], ['name', 'twitter:description', description],
  ]) {
    let meta = document.head.querySelector(`meta[${attribute}="${key}"]`);
    if (!meta) { meta = document.createElement('meta'); meta.setAttribute(attribute, key); document.head.append(meta); }
    meta.content = value;
  }
}
