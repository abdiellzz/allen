// Contenido editorial de refuerzo, sin generación ni ejecución en el dispositivo.
export const reinforcementContent = [
 {
  "courseId": "fractions-v1",
  "id": "math-decimal",
  "title": "De fracciones a decimales",
  "prerequisite": "parts",
  "module": "Números cotidianos",
  "explanation": "Un decimal representa partes de una unidad: décimas, centésimas y milésimas. Para convertir una fracción a decimal, divide el numerador entre el denominador.",
  "example": "3/4 = 3 ÷ 4 = 0.75. Son 75 centésimas.",
  "alternative": "1/2 = 0.5: media unidad equivale a cinco décimas.",
  "items": [
   [
    "input",
    "Escribe 1/4 como decimal.",
    [
     "0.25",
     "0.4",
     "4"
    ],
    "1 ÷ 4 = 0.25; cuatro cuartos forman 1.",
    {
     "numeric": true
    }
   ],
   [
    "match",
    "Relaciona cada fracción con su decimal.",
    [
     [
      "1/2",
      "0.5"
     ],
     [
      "3/4",
      "0.75"
     ],
     [
      "1/5",
      "0.2"
     ]
    ],
    "Dividir el numerador entre el denominador da 0.5, 0.75 y 0.2.",
    {}
   ],
   [
    "choice",
    "¿Qué decimal representa 7/10?",
    [
     "0.7",
     "0.07",
     "7.0"
    ],
    "7/10 son siete décimas: 0.7. El primer lugar después del punto representa décimas.",
    {
     "feedbackByAnswer": {
      "0.07": "0.07 son siete centésimas, no décimas.",
      "7.0": "7.0 son siete unidades enteras."
     }
    }
   ]
  ]
 },
 {
  "courseId": "fractions-v1",
  "id": "math-decimal-add",
  "title": "Sumar y restar decimales",
  "prerequisite": "math-decimal",
  "module": "Números cotidianos",
  "explanation": "Alinea unidades con unidades y décimas con décimas. Puedes añadir ceros a la derecha de la parte decimal sin cambiar el valor.",
  "example": "2.30 + 1.45 = 3.75. Alinea el punto decimal antes de sumar.",
  "alternative": "5.00 − 1.25 = 3.75; añadir ceros facilita alinear posiciones.",
  "items": [
   [
    "order",
    "Ordena el procedimiento para sumar 1.2 + 0.35.",
    [
     "Escribir 1.20 y 0.35",
     "Alinear los puntos decimales",
     "Sumar y obtener 1.55"
    ],
    "Los valores se alinean por posición, no por el último dígito.",
    {}
   ],
   [
    "input",
    "Una libreta cuesta 1.50 y un lápiz 0.25. Escribe el total.",
    [
     "1.75",
     "1.525",
     "1.25"
    ],
    "1.50 + 0.25 = 1.75. Alinea el punto decimal y suma las cifras de cada posición.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "¿Cuánto es 4.8 − 1.25?",
    [
     "3.55",
     "3.63",
     "4.55"
    ],
    "4.80 − 1.25 = 3.55. Alinea las posiciones decimales antes de restar.",
    {}
   ]
  ]
 },
 {
  "courseId": "fractions-v1",
  "id": "math-percent",
  "title": "Porcentajes en la vida diaria",
  "prerequisite": "math-decimal-add",
  "module": "Números cotidianos",
  "explanation": "Un porcentaje expresa partes de cada 100. Para calcular p% de una cantidad, multiplica por p/100. Un descuento se resta del precio inicial.",
  "example": "20% de 50 = 0.20 × 50 = 10. Con ese descuento, pagas 40.",
  "alternative": "10% de 80 es 8; la décima parte de una cantidad.",
  "items": [
   [
    "match",
    "Relaciona porcentajes y fracciones.",
    [
     [
      "50%",
      "1/2"
     ],
     [
      "25%",
      "1/4"
     ],
     [
      "10%",
      "1/10"
     ]
    ],
    "Cada porcentaje se escribe sobre 100 y se simplifica.",
    {}
   ],
   [
    "input",
    "Calcula 25% de 40.",
    [
     "10",
     "25",
     "15"
    ],
    "25/100 × 40 = 10. Un 25% equivale a la cuarta parte de la cantidad.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "Una mochila de 60 tiene descuento del 10%. ¿Cuánto pagas?",
    [
     "54",
     "6",
     "50"
    ],
    "El descuento es 6; el precio final es 60 − 6 = 54.",
    {
     "feedbackByAnswer": {
      "6": "Calculaste el descuento, pero falta restarlo del precio.",
      "50": "10% no significa restar diez unidades."
     }
    }
   ]
  ]
 },
 {
  "courseId": "fractions-v1",
  "id": "math-ratio",
  "title": "Proporciones y recetas",
  "prerequisite": "math-percent",
  "module": "Números cotidianos",
  "explanation": "Si una receta se multiplica por un factor, multiplica todas sus cantidades por el mismo factor. Así se mantiene la proporción.",
  "example": "Para 2 personas usas 3 tazas. Para 6 personas, el factor es 6 ÷ 2 = 3: necesitas 9 tazas.",
  "alternative": "Si duplicas las personas de 4 a 8, duplicas también 2 vasos de agua a 4.",
  "items": [
   [
    "order",
    "Ordena cómo adaptar de 2 a 6 personas.",
    [
     "Calcular el factor: 6 ÷ 2",
     "Multiplicar cada ingrediente por 3",
     "Comprobar que todos usaron el mismo factor"
    ],
    "La proporción exige aplicar el mismo factor a todas las cantidades.",
    {}
   ],
   [
    "input",
    "Para 3 personas usas 2 tazas. ¿Cuántas necesitas para 9?",
    [
     "6",
     "3",
     "9"
    ],
    "El factor es 9 ÷ 3 = 3; 2 × 3 = 6 tazas.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "4 cuadernos cuestan 8. Al mismo precio unitario, ¿cuánto cuestan 6?",
    [
     "12",
     "10",
     "16"
    ],
    "Cada cuaderno cuesta 2; seis cuestan 12.",
    {}
   ]
  ]
 },
 {
  "courseId": "fractions-v1",
  "id": "math-integers",
  "title": "Números positivos y negativos",
  "prerequisite": "parts",
  "module": "Álgebra y medidas",
  "explanation": "Los números negativos están por debajo de cero. En una recta numérica, avanzar a la derecha aumenta el valor y a la izquierda lo disminuye.",
  "example": "−3 + 5 = 2: desde −3 avanzas cinco unidades a la derecha.",
  "alternative": "Una temperatura de −2 sube 4 grados: llega a 2.",
  "items": [
   [
    "input",
    "La temperatura es −4 y sube 6 grados. Escribe la temperatura final.",
    [
     "2",
     "-10",
     "10"
    ],
    "−4 + 6 = 2. Desde −4 avanza seis lugares hacia la derecha en la recta numérica.",
    {
     "numeric": true
    }
   ],
   [
    "error",
    "Señala el cálculo incorrecto.",
    [
     "−2 + 5 = −7",
     "−2 + 5 = 3",
     "5 − 7 = −2"
    ],
    "−2 + 5 = 3. Sumar un positivo desplaza a la derecha.",
    {}
   ],
   [
    "choice",
    "¿Cuál número es mayor?",
    [
     "-1",
     "-5",
     "-8"
    ],
    "−1 está más a la derecha y más cerca de cero que −5 y −8.",
    {}
   ]
  ]
 },
 {
  "courseId": "fractions-v1",
  "id": "math-equation",
  "title": "Resolver una ecuación sencilla",
  "prerequisite": "math-integers",
  "module": "Álgebra y medidas",
  "explanation": "Una ecuación afirma que dos expresiones son iguales. Para conservar la igualdad, aplica la misma operación a ambos lados.",
  "example": "x + 4 = 9. Resta 4 en ambos lados: x = 5. Comprueba: 5 + 4 = 9.",
  "alternative": "2x = 10. Divide ambos lados por 2: x = 5.",
  "items": [
   [
    "order",
    "Ordena la solución de x + 3 = 8.",
    [
     "Restar 3 en ambos lados",
     "Obtener x = 5",
     "Comprobar que 5 + 3 = 8"
    ],
    "Usamos la operación inversa y verificamos sustituyendo el valor.",
    {}
   ],
   [
    "input",
    "Resuelve x + 6 = 14. Escribe x.",
    [
     "8",
     "20",
     "6"
    ],
    "Resta 6 en ambos lados: x = 8. Comprueba sustituyendo: 8 + 6 = 14.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "En 3x = 21, ¿cuánto vale x?",
    [
     "7",
     "18",
     "63"
    ],
    "Divide ambos lados por 3: x = 7.",
    {}
   ]
  ]
 },
 {
  "courseId": "fractions-v1",
  "id": "math-area",
  "title": "Área y perímetro",
  "prerequisite": "math-equation",
  "module": "Álgebra y medidas",
  "explanation": "El perímetro mide el contorno y usa unidades de longitud. El área mide la superficie y usa unidades cuadradas. En un rectángulo, área = base × altura.",
  "example": "Un rectángulo de 5 cm por 3 cm tiene área 15 cm² y perímetro 2 × (5 + 3) = 16 cm.",
  "alternative": "Un cuadrado de lado 4 m tiene área 16 m² y perímetro 16 m; coinciden los números, no las unidades.",
  "items": [
   [
    "match",
    "Relaciona cada medida con su significado.",
    [
     [
      "Perímetro",
      "Contorno"
     ],
     [
      "Área",
      "Superficie"
     ],
     [
      "cm²",
      "Unidad de área"
     ]
    ],
    "No confundas longitud del borde con superficie interior.",
    {}
   ],
   [
    "input",
    "Un rectángulo mide 6 m por 2 m. Escribe su área en m², solo el número.",
    [
     "12",
     "16",
     "8"
    ],
    "6 × 2 = 12 m². Multiplica largo por ancho para contar las unidades cuadradas.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "Un rectángulo de 7 cm por 2 cm tiene perímetro de…",
    [
     "18 cm",
     "14 cm²",
     "9 cm"
    ],
    "2 × (7 + 2) = 18 cm. El perímetro suma las longitudes de los cuatro lados.",
    {
     "feedbackByAnswer": {
      "14 cm²": "Calculaste el área; se pidió el contorno.",
      "9 cm": "Sumaste dos lados; faltan los otros dos."
     }
    }
   ]
  ]
 },
 {
  "courseId": "fractions-v1",
  "id": "math-average",
  "title": "Promedio y lectura de datos",
  "prerequisite": "math-area",
  "module": "Álgebra y medidas",
  "explanation": "La media aritmética se obtiene sumando los valores y dividiendo entre cuántos hay. Una media resume los datos, pero no muestra toda su variación.",
  "example": "La media de 4, 6 y 8 es (4 + 6 + 8) ÷ 3 = 6.",
  "alternative": "Dos grupos pueden tener media 5: [5, 5] y [0, 10], aunque su variación es distinta.",
  "items": [
   [
    "order",
    "Ordena cómo calcular la media de 3, 5 y 7.",
    [
     "Sumar: 3 + 5 + 7 = 15",
     "Contar los valores: hay 3",
     "Dividir: 15 ÷ 3 = 5"
    ],
    "La media requiere suma y número de observaciones.",
    {}
   ],
   [
    "input",
    "Calcula la media de 2, 4 y 9.",
    [
     "5",
     "15",
     "3"
    ],
    "(2 + 4 + 9) ÷ 3 = 5. Suma los tres datos y divide entre la cantidad de datos.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "Dos grupos tienen la misma media. ¿Qué puedes concluir?",
    [
     "Comparten la media, pero pueden tener distinta variación",
     "Todos sus datos son iguales",
     "Tienen la misma cantidad de datos"
    ],
    "La media por sí sola no describe todos los datos.",
    {}
   ]
  ]
 },
 {
  "courseId": "reading-v1",
  "id": "reading-context",
  "title": "Vocabulario por contexto",
  "prerequisite": "reading-main",
  "module": "Comprender textos",
  "explanation": "Para entender una palabra desconocida, observa las pistas de la oración y comprueba qué significado mantiene el sentido.",
  "example": "«El camino era estrecho: solo cabía una persona». Estrecho significa poco ancho.",
  "alternative": "«Mara estaba exhausta después de correr; necesitó descansar». Exhausta significa muy cansada.",
  "items": [
   [
    "input",
    "«El suelo estaba húmedo después de la lluvia». Húmedo significa un poco ___.",
    [
     "mojado",
     "seco",
     "duro"
    ],
    "La lluvia aporta la pista: húmedo es un poco mojado.",
    {}
   ],
   [
    "choice",
    "«El salón estaba vacío; nadie había llegado». ¿Qué significa vacío aquí?",
    [
     "Sin personas",
     "Muy ruidoso",
     "Lleno de alumnos"
    ],
    "Nadie había llegado indica ausencia de personas.",
    {}
   ],
   [
    "choice",
    "«Fue un gesto generoso: compartió su merienda». Generoso se relaciona con…",
    [
     "Compartir con otros",
     "Ocultar algo",
     "Competir siempre"
    ],
    "Compartir la merienda es la evidencia del significado.",
    {}
   ]
  ],
  "guide": {
   "kind": "text",
   "lines": [
    [
     "El suelo estaba húmedo.",
     "Húmedo describe presencia de agua."
    ],
    [
     "Había llovido toda la noche.",
     "La lluvia justifica el significado en este contexto."
    ]
   ]
  }
 },
 {
  "courseId": "reading-v1",
  "id": "reading-cause",
  "title": "Causas y consecuencias",
  "prerequisite": "reading-context",
  "module": "Comprender textos",
  "explanation": "Una causa explica por qué ocurre algo. Una consecuencia es lo que sucede como resultado. Conectores como porque y por eso ayudan a reconocer la relación.",
  "example": "«Llovió mucho, por eso se suspendió el partido». La lluvia es causa; la suspensión, consecuencia.",
  "alternative": "«Estudió con práctica, por eso comprendió mejor». Practicar es la causa indicada.",
  "items": [
   [
    "match",
    "Relaciona cada parte del texto.",
    [
     [
      "Llovió mucho",
      "Causa"
     ],
     [
      "Se suspendió el partido",
      "Consecuencia"
     ],
     [
      "Por eso",
      "Conector"
     ]
    ],
    "El conector une la causa con su resultado.",
    {}
   ],
   [
    "choice",
    "«La planta se secó porque no recibió agua». ¿Cuál es la causa?",
    [
     "No recibió agua",
     "La planta se secó",
     "Recibió demasiada luz"
    ],
    "Porque introduce la causa; no inventamos otra que el texto no dice.",
    {}
   ],
   [
    "choice",
    "«Se apagó la luz y por eso dejaron de leer». ¿Cuál es la consecuencia?",
    [
     "Dejaron de leer",
     "Se apagó la luz",
     "Llegó un docente"
    ],
    "Dejar de leer es el resultado indicado.",
    {}
   ]
  ]
 },
 {
  "courseId": "reading-v1",
  "id": "reading-inference",
  "title": "Inferencias con evidencia",
  "prerequisite": "reading-cause",
  "module": "Comprender textos",
  "explanation": "Inferir es combinar pistas del texto con lo que sabes para formular una conclusión razonable. Una inferencia debe apoyarse en evidencia; no permite inventar cualquier detalle.",
  "example": "«Ana entró con paraguas mojado». Podemos inferir que probablemente llovía afuera, pero no sabemos en qué calle estaba.",
  "alternative": "«Luis bostezó varias veces». Puede estar cansado; el texto no demuestra cuántas horas durmió.",
  "items": [
   [
    "choice",
    "«Mara tomó un abrigo antes de salir». ¿Qué inferencia es razonable?",
    [
     "Puede esperar frío",
     "Seguro viaja a otro país",
     "Está buscando comida"
    ],
    "El abrigo apoya la posibilidad de frío, no demuestra un viaje.",
    {}
   ],
   [
    "error",
    "Señala la conclusión que inventa información.",
    [
     "Ana vive en la calle Central porque trae paraguas",
     "El paraguas mojado puede indicar lluvia",
     "El texto no dice dónde vive Ana"
    ],
    "El paraguas no aporta evidencia de una dirección.",
    {}
   ],
   [
    "choice",
    "Un personaje tiembla y busca una manta. ¿Qué apoya mejor el texto?",
    [
     "Probablemente tiene frío",
     "Tiene exactamente 39 grados de fiebre",
     "La manta es roja"
    ],
    "Las dos pistas apoyan frío; temperatura y color no se mencionan.",
    {}
   ]
  ]
 },
 {
  "courseId": "reading-v1",
  "id": "reading-fact",
  "title": "Hechos y opiniones",
  "prerequisite": "reading-inference",
  "module": "Comprender textos",
  "explanation": "Un hecho puede comprobarse con evidencia. Una opinión expresa una valoración o preferencia. Ambas pueden aparecer en un mismo texto.",
  "example": "«La biblioteca abre a las ocho» es verificable. «Es el lugar más bonito» expresa una valoración.",
  "alternative": "«El libro tiene 120 páginas» es comprobable; «es divertidísimo» depende de la valoración del lector.",
  "items": [
   [
    "match",
    "Clasifica cada afirmación.",
    [
     [
      "El libro tiene 120 páginas",
      "Hecho verificable"
     ],
     [
      "Es el mejor libro",
      "Opinión"
     ],
     [
      "Abre a las ocho",
      "Horario comprobable"
     ]
    ],
    "Distingue datos comprobables de valoraciones personales.",
    {}
   ],
   [
    "choice",
    "¿Cuál frase expresa una opinión?",
    [
     "Esta película es maravillosa",
     "La película dura 90 minutos",
     "La entrada cuesta 3"
    ],
    "Maravillosa expresa una valoración.",
    {}
   ],
   [
    "choice",
    "¿Cómo compruebas «La biblioteca abre a las ocho»?",
    [
     "Consultando su horario oficial",
     "Contando cuántos amigos lo creen",
     "Eligiendo la frase más bonita"
    ],
    "Una fuente pertinente permite verificar el dato.",
    {}
   ]
  ]
 },
 {
  "courseId": "reading-v1",
  "id": "writing-sentence",
  "title": "Oraciones completas",
  "prerequisite": "reading-main",
  "module": "Escribir con claridad",
  "explanation": "Una oración comunica una idea completa. En muchos casos puedes identificar de quién se habla y qué se dice de esa persona o cosa.",
  "example": "«La estudiante resolvió el problema». Se habla de la estudiante y se dice que resolvió el problema.",
  "alternative": "«Después del recreo» deja pendiente qué ocurrió; «Después del recreo, empezó la clase» completa la idea.",
  "items": [
   [
    "order",
    "Ordena estas partes para formar una oración.",
    [
     "La estudiante",
     "resolvió",
     "el problema"
    ],
    "El orden construye una idea completa: quién, acción y complemento.",
    {}
   ],
   [
    "choice",
    "¿Qué expresión presenta una idea completa?",
    [
     "Los niños leen en la biblioteca",
     "Después de la clase",
     "El cuaderno azul de"
    ],
    "Las otras expresiones dejan información esencial pendiente.",
    {}
   ],
   [
    "choice",
    "¿Qué completa «El perro…» como una oración?",
    [
     "corrió por el jardín.",
     "del vecino.",
     "muy pequeño."
    ],
    "Corrió por el jardín expresa qué hizo el perro.",
    {}
   ]
  ]
 },
 {
  "courseId": "reading-v1",
  "id": "writing-punctuation",
  "title": "Puntos y comas",
  "prerequisite": "writing-sentence",
  "module": "Escribir con claridad",
  "explanation": "El punto cierra una oración. La coma puede separar elementos de una enumeración. La puntuación ayuda a organizar las ideas y evitar confusiones.",
  "example": "«Traje lápices, hojas y colores. Después comencé el dibujo». Las comas separan elementos; el punto cierra una idea.",
  "alternative": "«Leí el texto. Luego respondí» contiene dos oraciones separadas por punto.",
  "items": [
   [
    "input",
    "Completa con el signo que cierra una oración: Hoy aprendí algo nuevo___",
    [
     ".",
     ";",
     ","
    ],
    "El punto cierra esta oración.",
    {}
   ],
   [
    "error",
    "Señala la enumeración que necesita comas.",
    [
     "Compré pan leche y fruta.",
     "Compré pan, leche y fruta.",
     "Compré fruta."
    ],
    "En una enumeración, las comas separan pan y leche; antes de y no se necesita aquí.",
    {}
   ],
   [
    "choice",
    "¿Qué versión separa claramente dos oraciones?",
    [
     "Llegué temprano. Abrí mi cuaderno.",
     "Llegué temprano abrí mi cuaderno",
     "Llegué. temprano abrí."
    ],
    "Cada oración comunica una idea completa y termina con punto.",
    {}
   ]
  ]
 },
 {
  "courseId": "reading-v1",
  "id": "writing-paragraph",
  "title": "Construir un párrafo",
  "prerequisite": "writing-punctuation",
  "module": "Escribir con claridad",
  "explanation": "Un párrafo desarrolla una idea central con detalles relacionados. Ordena la presentación, el desarrollo y un cierre que conecte con la idea.",
  "example": "Idea: leer ayuda a aprender. Desarrollo: permite conocer palabras y comparar ideas. Cierre: por eso conviene leer con frecuencia.",
  "alternative": "Un párrafo sobre cuidar el agua puede explicar cerrar el grifo y reparar fugas, sin saltar a un tema distinto.",
  "items": [
   [
    "order",
    "Ordena las partes de un párrafo explicativo.",
    [
     "Presentar la idea central",
     "Añadir detalles relacionados",
     "Cerrar conectando con la idea"
    ],
    "El orden orienta al lector y mantiene el tema.",
    {}
   ],
   [
    "choice",
    "Un párrafo trata del ahorro de agua. ¿Qué detalle corresponde?",
    [
     "Reparar una fuga evita desperdicio",
     "Mi color favorito es azul",
     "La bicicleta tiene dos ruedas"
    ],
    "El detalle desarrolla el mismo tema.",
    {}
   ],
   [
    "choice",
    "¿Qué mejora un párrafo con ideas de temas distintos?",
    [
     "Conservar las relacionadas y separar los otros temas",
     "Añadir más temas sin conexión",
     "Quitar toda explicación"
    ],
    "La unidad del párrafo exige detalles relacionados con su idea central.",
    {}
   ]
  ]
 },
 {
  "courseId": "reading-v1",
  "id": "writing-revise",
  "title": "Revisar antes de entregar",
  "prerequisite": "writing-paragraph",
  "module": "Escribir con claridad",
  "explanation": "Revisar incluye comprobar el sentido, el orden y la forma. Lee tu texto, verifica si responde al objetivo y corrige frases confusas, puntuación y repeticiones.",
  "example": "Antes de entregar una explicación, comprueba que tenga una idea central, un ejemplo pertinente y un cierre.",
  "alternative": "Si repetiste una palabra cinco veces, busca si puedes reformular sin cambiar el sentido.",
  "items": [
   [
    "order",
    "Ordena una revisión útil.",
    [
     "Leer y comprobar el objetivo",
     "Corregir ideas y organización",
     "Revisar puntuación y palabras"
    ],
    "Primero comprueba el sentido; después pule la forma.",
    {}
   ],
   [
    "choice",
    "Tu texto no responde a la pregunta. ¿Qué priorizas?",
    [
     "Revisar el contenido para responderla",
     "Solo cambiar la tipografía",
     "Agregar adornos"
    ],
    "La presentación no corrige un contenido que no responde al objetivo.",
    {}
   ],
   [
    "choice",
    "¿Qué prueba ayuda a detectar una frase confusa?",
    [
     "Leerla en voz alta y comprobar su sentido",
     "Entregar sin releer",
     "Cambiar todas las palabras por largas"
    ],
    "La revisión debe facilitar la comprensión, no complicarla.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-articles",
  "title": "A, an y palabras cotidianas",
  "prerequisite": "english-am",
  "module": "Inglés cotidiano",
  "explanation": "A y an acompañan a sustantivos contables singulares cuando hablamos de uno no identificado. Usa an antes de sonido vocálico y a antes de sonido consonántico.",
  "example": "A book, an apple. Lo que importa es el sonido: an hour, porque la h no se pronuncia.",
  "alternative": "A university usa a porque university empieza con sonido consonántico /y/.",
  "items": [
   [
    "input",
    "Completa: I have ___ apple.",
    [
     "an",
     "a",
     "the"
    ],
    "Apple empieza con sonido vocálico: an apple.",
    {}
   ],
   [
    "match",
    "Relaciona cada sustantivo con su artículo.",
    [
     [
      "book",
      "a"
     ],
     [
      "apple",
      "an"
     ],
     [
      "hour",
      "an (h muda)"
     ]
    ],
    "Book empieza con consonante; apple con vocal; hour tiene h muda.",
    {}
   ],
   [
    "choice",
    "¿Cuál expresión es correcta?",
    [
     "a university",
     "an university",
     "a apple"
    ],
    "University empieza con sonido /y/, por eso usa a.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-plurals",
  "title": "Singular y plural",
  "prerequisite": "english-articles",
  "module": "Inglés cotidiano",
  "explanation": "Muchos sustantivos forman plural con s. Algunos terminados en s, sh o ch añaden es. Hay plurales irregulares que se aprenden aparte.",
  "example": "Book → books. Box → boxes. Child → children es irregular.",
  "alternative": "One pencil, two pencils: dos lápices requieren plural.",
  "items": [
   [
    "input",
    "Escribe el plural de book.",
    [
     "books",
     "bookes",
     "book"
    ],
    "Book añade s: books.",
    {}
   ],
   [
    "match",
    "Relaciona singular y plural.",
    [
     [
      "box",
      "boxes"
     ],
     [
      "child",
      "children"
     ],
     [
      "pencil",
      "pencils"
     ]
    ],
    "Boxes añade es; children es irregular; pencils añade s.",
    {}
   ],
   [
    "choice",
    "Completa: I have two ___.",
    [
     "apples",
     "apple",
     "an apple"
    ],
    "Two indica más de una: apples.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-there",
  "title": "There is y there are",
  "prerequisite": "english-plurals",
  "module": "Inglés cotidiano",
  "explanation": "There is expresa que hay una cosa singular. There are se usa con plural. En estas prácticas trabajamos objetos contables.",
  "example": "There is a book on the desk. There are two books on the desk.",
  "alternative": "There is a chair: hay una silla. There are three chairs: hay tres sillas.",
  "items": [
   [
    "input",
    "Completa: There ___ two pencils.",
    [
     "are",
     "is",
     "am"
    ],
    "Two pencils es plural: there are.",
    {}
   ],
   [
    "error",
    "Señala la oración incorrecta.",
    [
     "There is three books.",
     "There is a book.",
     "There are three books."
    ],
    "Three books es plural y necesita there are.",
    {}
   ],
   [
    "choice",
    "¿Cómo dices Hay una silla?",
    [
     "There is a chair.",
     "There are a chair.",
     "I am a chair."
    ],
    "There is a chair expresa existencia singular.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-place",
  "title": "Preposiciones de lugar",
  "prerequisite": "english-there",
  "module": "Inglés cotidiano",
  "explanation": "In significa dentro de; on, sobre una superficie; under, debajo de. Elige según la relación entre los objetos.",
  "example": "The book is on the desk: el libro está sobre el escritorio.",
  "alternative": "The bag is under the chair: la mochila está debajo de la silla.",
  "items": [
   [
    "match",
    "Relaciona cada preposición.",
    [
     [
      "in",
      "Dentro de"
     ],
     [
      "on",
      "Sobre"
     ],
     [
      "under",
      "Debajo de"
     ]
    ],
    "Cada palabra expresa una relación espacial distinta.",
    {}
   ],
   [
    "input",
    "El lápiz está dentro de la caja: The pencil is ___ the box.",
    [
     "in",
     "on",
     "under"
    ],
    "Dentro de se expresa con in.",
    {}
   ],
   [
    "choice",
    "The ball is under the table significa…",
    [
     "La pelota está debajo de la mesa",
     "La pelota está dentro de la mesa",
     "La pelota está encima de la mesa"
    ],
    "Under significa debajo de.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-can",
  "title": "Habilidades con can",
  "prerequisite": "english-am",
  "module": "Conversar y comprender",
  "explanation": "Can expresa capacidad. Después de can usa el verbo base, sin to. Para negar usa cannot o can’t.",
  "example": "I can swim. She can read. El verbo después de can no cambia por la persona.",
  "alternative": "I cannot drive significa No puedo conducir.",
  "items": [
   [
    "input",
    "Completa: She ___ swim. Usa la palabra para expresar capacidad.",
    [
     "can",
     "is",
     "has"
    ],
    "She can swim expresa que sabe o puede nadar.",
    {}
   ],
   [
    "order",
    "Ordena una frase sobre capacidad.",
    [
     "I",
     "can",
     "read"
    ],
    "I can read usa el verbo base después de can.",
    {}
   ],
   [
    "choice",
    "¿Qué oración es correcta?",
    [
     "He can play.",
     "He can plays.",
     "He can to play."
    ],
    "Después de can se usa play, sin s ni to.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-wh-questions",
  "title": "Preguntas con what y where",
  "prerequisite": "english-can",
  "module": "Conversar y comprender",
  "explanation": "What pregunta qué o cuál; where pregunta dónde. Observa el tipo de información que necesitas.",
  "example": "What is your name? pregunta el nombre. Where is the library? pregunta una ubicación.",
  "alternative": "Where do you live? pregunta dónde vives, no tu nombre.",
  "items": [
   [
    "match",
    "Relaciona la pregunta con la información.",
    [
     [
      "What is your name?",
      "Nombre"
     ],
     [
      "Where is the library?",
      "Ubicación"
     ],
     [
      "What is this?",
      "Identificación"
     ]
    ],
    "La palabra interrogativa orienta el tipo de respuesta.",
    {}
   ],
   [
    "input",
    "Completa para preguntar ubicación: ___ is the school?",
    [
     "Where",
     "What",
     "Who"
    ],
    "Where pregunta dónde está la escuela.",
    {}
   ],
   [
    "choice",
    "¿Qué pregunta corresponde a la respuesta My name is Ana?",
    [
     "What is your name?",
     "Where is the library?",
     "Can you swim?"
    ],
    "La respuesta proporciona un nombre.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-connectors",
  "title": "And, but y because",
  "prerequisite": "english-wh-questions",
  "module": "Conversar y comprender",
  "explanation": "And añade una idea; but introduce contraste; because da una razón. Elegir el conector adecuado cambia cómo se relacionan las ideas.",
  "example": "I like tea and water añade dos preferencias. I am tired but happy contrasta. I rest because I am tired da una razón.",
  "alternative": "I study because I want to learn: la segunda parte explica por qué estudio.",
  "items": [
   [
    "match",
    "Relaciona conector y función.",
    [
     [
      "and",
      "Añadir"
     ],
     [
      "but",
      "Contrastar"
     ],
     [
      "because",
      "Explicar una razón"
     ]
    ],
    "Los conectores expresan relaciones diferentes.",
    {}
   ],
   [
    "input",
    "Completa con el conector de causa: I rest ___ I am tired.",
    [
     "because",
     "and",
     "but"
    ],
    "Because introduce la razón del descanso.",
    {}
   ],
   [
    "choice",
    "Quiero decir Estoy cansado, pero feliz. ¿Qué conector uso?",
    [
     "but",
     "because",
     "and"
    ],
    "But expresa el contraste entre cansado y feliz.",
    {}
   ]
  ]
 },
 {
  "courseId": "english-v1",
  "id": "english-reading",
  "title": "Leer un mensaje breve",
  "prerequisite": "english-connectors",
  "module": "Conversar y comprender",
  "explanation": "En un mensaje breve, identifica quién habla, qué hará y cuándo. Busca palabras clave y usa el contexto sin traducir cada palabra por separado.",
  "example": "Message: Hi Ana. Meet me at the library at three. —Luis. Luis propone encontrarse en la biblioteca a las tres.",
  "alternative": "Please bring your book tomorrow pide llevar el libro mañana.",
  "items": [
   [
    "choice",
    "«Meet me at the library at three». ¿Dónde es el encuentro?",
    [
     "En la biblioteca",
     "En la escuela de música",
     "En casa de Luis"
    ],
    "At the library indica el lugar.",
    {}
   ],
   [
    "input",
    "«Please bring your book tomorrow». Tomorrow significa ___.",
    [
     "mañana",
     "ayer",
     "hoy"
    ],
    "Tomorrow es mañana.",
    {}
   ],
   [
    "choice",
    "«The class starts at nine». ¿Qué informa?",
    [
     "La clase empieza a las nueve",
     "La clase dura nueve horas",
     "Hay nueve estudiantes"
    ],
    "Starts indica comenzar y at nine señala la hora.",
    {}
   ]
  ],
  "guide": {
   "kind": "text",
   "lines": [
    [
     "Meet me at the library.",
     "La biblioteca es el lugar del encuentro."
    ],
    [
     "At three.",
     "Three indica la hora: las tres."
    ]
   ]
  }
 },
 {
  "courseId": "python-v1",
  "id": "python-types",
  "title": "Tipos de datos",
  "prerequisite": "python-values",
  "module": "Pensar con código",
  "explanation": "Los números, los textos y los booleanos representan datos distintos. Las comillas crean texto. True y False son valores booleanos de Python.",
  "example": "7 es entero; \"7\" es texto; True es booleano. No significan lo mismo para las operaciones.",
  "alternative": "3.5 es un número decimal; \"Hola\" es texto.",
  "items": [
   [
    "match",
    "Relaciona valor y tipo.",
    [
     [
      "7",
      "Entero"
     ],
     [
      "\"7\"",
      "Texto"
     ],
     [
      "True",
      "Booleano"
     ]
    ],
    "Las comillas distinguen texto; True representa un valor lógico.",
    {}
   ],
   [
    "input",
    "El literal \"Hola\" es una cadena de ___.",
    [
     "texto",
     "números",
     "booleanos"
    ],
    "Las comillas delimitan una cadena de texto.",
    {}
   ],
   [
    "error",
    "Señala la afirmación incorrecta.",
    [
     "\"5\" es un entero",
     "5 es un entero",
     "False es booleano"
    ],
    "\"5\" es texto porque está entre comillas.",
    {}
   ]
  ]
 },
 {
  "courseId": "python-v1",
  "id": "python-arithmetic",
  "title": "Operaciones y prioridad",
  "prerequisite": "python-types",
  "module": "Pensar con código",
  "explanation": "Python calcula multiplicaciones y divisiones antes que sumas y restas. Los paréntesis permiten elegir otro agrupamiento.",
  "example": "2 + 3 * 4 da 14; (2 + 3) * 4 da 20.",
  "alternative": "10 - 2 * 3 da 4: primero calcula 2 * 3.",
  "items": [
   [
    "order",
    "Ordena la evaluación de 2 + 3 * 4.",
    [
     "Calcular 3 * 4 = 12",
     "Sumar 2 + 12",
     "Obtener 14"
    ],
    "La multiplicación tiene prioridad.",
    {}
   ],
   [
    "input",
    "¿Qué muestra print((2 + 3) * 4)?",
    [
     "20",
     "14",
     "24"
    ],
    "El paréntesis se calcula primero: 5 * 4 = 20.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "¿Qué muestra print(10 - 2 * 3)?",
    [
     "4",
     "24",
     "18"
    ],
    "Primero 2 * 3 = 6; luego 10 - 6 = 4.",
    {}
   ]
  ],
  "guide": {
   "kind": "code",
   "lines": [
    [
     "subtotal = 3 * 4",
     "Multiplica primero: subtotal vale 12."
    ],
    [
     "total = 2 + subtotal",
     "Suma después: total vale 14."
    ],
    [
     "print(total)",
     "Muestra 14; no ejecutamos código del estudiante."
    ]
   ]
  }
 },
 {
  "courseId": "python-v1",
  "id": "python-compare",
  "title": "Comparar y decidir",
  "prerequisite": "python-arithmetic",
  "module": "Pensar con código",
  "explanation": "== comprueba igualdad; > y < comparan magnitudes. Una comparación produce True o False. No confundas == con =, que asigna.",
  "example": "puntos = 5 asigna un valor. puntos == 5 comprueba igualdad y produce True.",
  "alternative": "3 > 7 produce False porque tres no es mayor que siete.",
  "items": [
   [
    "match",
    "Relaciona símbolo y función.",
    [
     [
      "=",
      "Asignar"
     ],
     [
      "==",
      "Comparar igualdad"
     ],
     [
      ">",
      "Mayor que"
     ]
    ],
    "Asignación y comparación son operaciones diferentes.",
    {}
   ],
   [
    "input",
    "Completa con el operador de igualdad: puntos ___ 5.",
    [
     "==",
     "=",
     ">"
    ],
    "== compara igualdad; = asigna.",
    {}
   ],
   [
    "choice",
    "¿Qué valor produce 4 < 9?",
    [
     "True",
     "False",
     "4"
    ],
    "La comparación es verdadera: cuatro es menor que nueve.",
    {}
   ]
  ]
 },
 {
  "courseId": "python-v1",
  "id": "python-trace",
  "title": "Seguir cambios de una variable",
  "prerequisite": "python-compare",
  "module": "Pensar con código",
  "explanation": "Para seguir un programa, procesa cada línea en orden y anota el valor actual. Una nueva asignación sustituye el valor anterior de ese nombre.",
  "example": "x = 2; x = x + 3; x = x * 2. Los valores de x son 2, 5 y 10.",
  "alternative": "puntos = 4; puntos = puntos - 1 deja puntos en 3.",
  "items": [
   [
    "order",
    "Ordena los valores de x al ejecutar x = 2; x = x + 3; x = x * 2.",
    [
     "x vale 2",
     "x vale 5",
     "x vale 10"
    ],
    "Cada instrucción usa el valor vigente de la variable.",
    {}
   ],
   [
    "input",
    "n = 3; n = n + 4; n = n - 2. Escribe el valor final de n.",
    [
     "5",
     "7",
     "3"
    ],
    "3 + 4 = 7; 7 - 2 = 5.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "a = 2; a = 8; print(a). ¿Qué se muestra?",
    [
     "8",
     "2",
     "10"
    ],
    "La segunda asignación reemplaza el valor anterior.",
    {}
   ]
  ],
  "guide": {
   "kind": "code",
   "lines": [
    [
     "x = 2",
     "Estado: x vale 2."
    ],
    [
     "x = x + 3",
     "Estado: x vale 5."
    ],
    [
     "x = x * 2",
     "Estado: x vale 10."
    ]
   ]
  }
 },
 {
  "courseId": "python-v1",
  "id": "python-lists",
  "title": "Listas y posiciones",
  "prerequisite": "python-values",
  "module": "Organizar programas",
  "explanation": "Una lista guarda una secuencia de valores. Los índices empiezan en cero: la primera posición es 0 y la segunda es 1.",
  "example": "colores = [\"rojo\", \"azul\", \"verde\"]. colores[0] es rojo; colores[1] es azul.",
  "alternative": "len([4, 5, 6]) devuelve 3: hay tres elementos.",
  "items": [
   [
    "input",
    "En [10, 20, 30], ¿qué índice tiene el primer elemento?",
    [
     "0",
     "1",
     "10"
    ],
    "Python comienza los índices en cero.",
    {
     "numeric": true
    }
   ],
   [
    "match",
    "Relaciona índice y valor en [10, 20, 30].",
    [
     [
      "0",
      "10"
     ],
     [
      "1",
      "20"
     ],
     [
      "2",
      "30"
     ]
    ],
    "El índice es la posición, no el valor almacenado.",
    {}
   ],
   [
    "choice",
    "¿Qué devuelve len([\"a\", \"b\", \"c\"])?",
    [
     "3",
     "2",
     "0"
    ],
    "len cuenta tres elementos.",
    {}
   ]
  ]
 },
 {
  "courseId": "python-v1",
  "id": "python-loop-list",
  "title": "Recorrer una lista",
  "prerequisite": "python-lists",
  "module": "Organizar programas",
  "explanation": "Un bucle for puede recorrer los elementos de una lista en orden. En cada vuelta, la variable del bucle recibe el siguiente elemento.",
  "example": "for n in [2, 4]:\n    print(n)\nMuestra 2 y después 4.",
  "alternative": "Recorrer [\"Ana\", \"Luis\"] permite trabajar primero con Ana y después con Luis.",
  "items": [
   [
    "order",
    "Ordena lo que muestra for n in [2, 4, 6]: print(n).",
    [
     "Muestra 2",
     "Muestra 4",
     "Muestra 6"
    ],
    "El bucle recorre los elementos en su orden.",
    {}
   ],
   [
    "input",
    "¿Cuántas vueltas hace for n in [5, 8, 9]?",
    [
     "3",
     "2",
     "9"
    ],
    "Hay tres elementos: tres vueltas.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "for n in [1, 3]: print(n + 1). ¿Qué muestra?",
    [
     "2 y después 4",
     "1 y después 3",
     "4 solamente"
    ],
    "Suma 1 a cada elemento durante su vuelta.",
    {}
   ]
  ]
 },
 {
  "courseId": "python-v1",
  "id": "python-functions",
  "title": "Funciones y resultados",
  "prerequisite": "python-loop-list",
  "module": "Organizar programas",
  "explanation": "Una función agrupa instrucciones reutilizables. Un parámetro recibe un dato. return devuelve un resultado al lugar donde se llamó la función.",
  "example": "def doble(n):\n    return n * 2\ndoble(4) devuelve 8.",
  "alternative": "Una función sumar(a, b) puede devolver a + b y usarse con números distintos.",
  "items": [
   [
    "match",
    "Relaciona elemento y papel.",
    [
     [
      "Parámetro",
      "Recibe un dato"
     ],
     [
      "return",
      "Devuelve un resultado"
     ],
     [
      "Llamada",
      "Usa la función"
     ]
    ],
    "Definir una función no equivale a llamarla.",
    {}
   ],
   [
    "input",
    "Si doble(n) devuelve n * 2, ¿qué devuelve doble(6)?",
    [
     "12",
     "6",
     "8"
    ],
    "Sustituye n por 6: 6 * 2 = 12.",
    {
     "numeric": true
    }
   ],
   [
    "choice",
    "¿Qué instrucción devuelve el resultado de una función?",
    [
     "return",
     "print solamente",
     "Un comentario"
    ],
    "return devuelve un valor; print solo muestra contenido.",
    {}
   ]
  ]
 },
 {
  "courseId": "python-v1",
  "id": "python-tests",
  "title": "Probar casos y límites",
  "prerequisite": "python-functions",
  "module": "Organizar programas",
  "explanation": "Una prueba compara un resultado esperado con el obtenido. Usa casos normales y límites relevantes; una sola prueba no demuestra que todo programa sea correcto.",
  "example": "Si una condición acepta puntos >= 10, prueba 9, 10 y 11 para revisar el límite.",
  "alternative": "Para una función que suma, prueba 2 + 3, valores cero y negativos si el objetivo los permite.",
  "items": [
   [
    "order",
    "Ordena una prueba útil.",
    [
     "Elegir entrada y resultado esperado",
     "Obtener el resultado del programa",
     "Comparar y revisar diferencias"
    ],
    "Definir lo esperado evita juzgar solo por apariencia.",
    {}
   ],
   [
    "choice",
    "Una condición es puntos >= 10. ¿Qué casos revisan el límite?",
    [
     "9, 10 y 11",
     "100, 200 y 300",
     "Solo 50"
    ],
    "Estos valores quedan antes, en y después del límite.",
    {}
   ],
   [
    "choice",
    "Una prueba salió bien. ¿Qué puedes afirmar?",
    [
     "Ese caso pasó; faltan otros casos relevantes",
     "Todo programa está libre de errores",
     "Las pruebas ya no sirven"
    ],
    "La evidencia de un caso no cubre todas las entradas.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-passphrase",
  "title": "Frases de contraseña",
  "prerequisite": "safe-accounts",
  "module": "Cuidar tu identidad",
  "explanation": "Una contraseña debe ser larga, única y difícil de predecir. Un gestor puede crear y guardar claves distintas. Los ejemplos públicos nunca deben usarse como claves reales.",
  "example": "Una frase de varias palabras elegidas al azar es más difícil de adivinar que tu nombre y año de nacimiento. No uses la frase de esta lección.",
  "alternative": "Si dos servicios comparten la misma clave, una filtración puede afectar ambos.",
  "items": [
   [
    "choice",
    "¿Qué estrategia es mejor?",
    [
     "Una clave larga y única por servicio",
     "Tu nombre más tu cumpleaños",
     "La misma clave en todas partes"
    ],
    "Longitud, imprevisibilidad y exclusividad reducen riesgos.",
    {}
   ],
   [
    "error",
    "Señala la práctica insegura.",
    [
     "Usar un ejemplo público de contraseña como clave real",
     "Crear claves únicas con un gestor",
     "Guardar códigos de recuperación en un lugar privado"
    ],
    "Un ejemplo conocido puede probarse fácilmente; nunca copies claves públicas.",
    {}
   ],
   [
    "choice",
    "¿Qué dato conviene evitar en una clave?",
    [
     "Tu fecha de nacimiento",
     "Palabras elegidas al azar",
     "Caracteres generados al azar"
    ],
    "Los datos personales suelen ser más predecibles.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-mfa",
  "title": "Verificación en dos pasos",
  "prerequisite": "digital-passphrase",
  "module": "Cuidar tu identidad",
  "explanation": "La verificación en dos pasos añade una comprobación además de la contraseña. Nunca compartas códigos con alguien que te los pide por chat. Guarda los códigos de recuperación de forma privada.",
  "example": "Una persona pide el código de tu aplicación autenticadora: no se lo das y verificas por un canal conocido.",
  "alternative": "Un código de recuperación permite recuperar acceso; trátalo como un secreto.",
  "items": [
   [
    "match",
    "Relaciona elemento y cuidado.",
    [
     [
      "Contraseña",
      "No reutilizar"
     ],
     [
      "Código autenticador",
      "No compartir por chat"
     ],
     [
      "Código de recuperación",
      "Guardar en privado"
     ]
    ],
    "Los tres protegen acceso y requieren cuidados distintos.",
    {}
   ],
   [
    "choice",
    "Supuesto soporte te pide el código de acceso. ¿Qué haces?",
    [
     "No compartirlo y verificar por un canal conocido",
     "Enviarlo rápido",
     "Publicarlo para pedir ayuda"
    ],
    "Soporte legítimo no necesita que compartas un código de inicio por chat.",
    {}
   ],
   [
    "choice",
    "¿Para qué sirve un código de recuperación?",
    [
     "Recuperar acceso cuando falta el segundo factor",
     "Aumentar seguidores",
     "Compartir la cuenta con cualquiera"
    ],
    "Es un secreto de recuperación, no un mensaje público.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-permissions",
  "title": "Permisos de aplicaciones",
  "prerequisite": "digital-mfa",
  "module": "Cuidar tu identidad",
  "explanation": "Un permiso da acceso a una capacidad o dato. Comprueba si es necesario para la función que vas a usar y revísalo cuando cambie tu necesidad.",
  "example": "Una grabadora necesita micrófono para grabar; una calculadora común no necesita tus contactos.",
  "alternative": "Puedes negar un permiso y reconsiderarlo si una función concreta lo necesita.",
  "items": [
   [
    "match",
    "Relaciona función y permiso pertinente.",
    [
     [
      "Grabar audio",
      "Micrófono"
     ],
     [
      "Tomar una foto",
      "Cámara"
     ],
     [
      "Mostrar un mapa con tu ubicación",
      "Ubicación"
     ]
    ],
    "La necesidad depende de la función usada, no de aceptar todo.",
    {}
   ],
   [
    "choice",
    "Una calculadora pide contactos sin explicar por qué. ¿Qué haces?",
    [
     "Revisar y negar si no es necesario",
     "Aceptar todos los permisos",
     "Compartir más datos para ayudar"
    ],
    "Un permiso debe tener una finalidad pertinente.",
    {}
   ],
   [
    "choice",
    "¿Cuándo revisar los permisos?",
    [
     "Al instalar y cuando cambien las funciones o necesidades",
     "Nunca después de aceptar",
     "Solo cuando el teléfono se rompe"
    ],
    "Los permisos también pueden ajustarse después.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-fraud",
  "title": "Verificar antes de confiar",
  "prerequisite": "digital-permissions",
  "module": "Cuidar tu identidad",
  "explanation": "La urgencia, premios inesperados y peticiones de secretos son señales para detenerte. Verifica desde una dirección o aplicación conocida, sin usar el enlace del mensaje sospechoso.",
  "example": "Un mensaje amenaza con cerrar tu cuenta. Abres la aplicación oficial por tu cuenta para comprobar el aviso.",
  "alternative": "Un premio exige pagar primero: detente y verifica quién lo ofrece.",
  "items": [
   [
    "order",
    "Ordena una respuesta a un mensaje sospechoso.",
    [
     "Detenerse sin abrir el enlace",
     "Consultar un canal oficial conocido",
     "Actuar según lo verificado"
    ],
    "La verificación se hace fuera del mensaje sospechoso.",
    {}
   ],
   [
    "choice",
    "¿Qué señal exige precaución?",
    [
     "Petición urgente de un código secreto",
     "Un horario escolar esperado",
     "Una explicación sin pedir datos"
    ],
    "La urgencia y los secretos son señales de posible engaño.",
    {}
   ],
   [
    "choice",
    "¿Cómo verificas un supuesto bloqueo bancario?",
    [
     "Abrir la aplicación oficial por tu cuenta",
     "Usar el enlace del mensaje",
     "Responder con tu PIN"
    ],
    "Evita depender del canal sospechoso para verificarlo.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-footprint",
  "title": "Huella digital y privacidad",
  "prerequisite": "safe-accounts",
  "module": "Usar tecnología con criterio",
  "explanation": "Tu huella digital incluye información que compartes y rastros de tus interacciones. Antes de publicar, piensa en audiencia, datos personales y posibilidad de que alguien guarde una copia.",
  "example": "Una foto puede mostrar una dirección en el fondo. Revisa los detalles antes de compartirla.",
  "alternative": "Borrar una publicación no garantiza que desaparezcan capturas o copias.",
  "items": [
   [
    "choice",
    "Antes de publicar una foto, ¿qué revisas?",
    [
     "Datos personales visibles y audiencia",
     "Solo cuántos likes tendrá",
     "Que muestre más información de la necesaria"
    ],
    "El fondo y la audiencia también afectan la privacidad.",
    {}
   ],
   [
    "error",
    "Señala la afirmación incorrecta.",
    [
     "Borrar garantiza que nadie conserve una copia",
     "Alguien puede hacer una captura",
     "Conviene revisar datos visibles antes de publicar"
    ],
    "Puede haber copias fuera de tu control.",
    {}
   ],
   [
    "choice",
    "¿Qué dato conviene ocultar en una publicación pública?",
    [
     "Tu dirección de casa",
     "Una explicación de un tema",
     "Un dibujo sin datos personales"
    ],
    "La dirección es información personal sensible.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-ai-check",
  "title": "Comprobar respuestas de IA",
  "prerequisite": "digital-footprint",
  "module": "Usar tecnología con criterio",
  "explanation": "Una respuesta generada puede sonar segura y estar equivocada. Comprueba afirmaciones importantes con fuentes pertinentes y distingue una explicación de evidencia validada.",
  "example": "Un chatbot cita un libro: verifica que el libro exista y que apoye la afirmación antes de usar la cita.",
  "alternative": "Si una respuesta no ofrece evidencia suficiente, reconoce el límite y busca una fuente del curso.",
  "items": [
   [
    "order",
    "Ordena una verificación de una respuesta generada.",
    [
     "Identificar la afirmación importante",
     "Consultar una fuente pertinente",
     "Comparar y reconocer límites"
    ],
    "La seguridad del tono no demuestra exactitud.",
    {}
   ],
   [
    "choice",
    "Una IA menciona una cita que no encuentras. ¿Qué haces?",
    [
     "No presentarla como verificada y buscar evidencia",
     "Inventar la fuente",
     "Copiarla porque suena profesional"
    ],
    "Una cita debe existir y apoyar lo que afirmas.",
    {}
   ],
   [
    "choice",
    "¿Qué prueba mejor una afirmación del curso?",
    [
     "Una fuente pertinente que la sustenta",
     "Que el chatbot use palabras difíciles",
     "Que la respuesta sea larga"
    ],
    "La evidencia importa más que el tono.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-update",
  "title": "Actualizaciones y cuidado",
  "prerequisite": "digital-ai-check",
  "module": "Usar tecnología con criterio",
  "explanation": "Las actualizaciones pueden corregir errores y vulnerabilidades. Instálalas desde canales oficiales y prepara una copia de datos importantes antes de cambios relevantes.",
  "example": "Una ventana desconocida te ofrece una actualización. Abres los ajustes oficiales del sistema para comprobarla.",
  "alternative": "Un archivo llamado actualización no demuestra que provenga del fabricante.",
  "items": [
   [
    "order",
    "Ordena una actualización prudente.",
    [
     "Comprobar el canal oficial",
     "Preparar una copia de datos importantes",
     "Instalar y verificar el funcionamiento"
    ],
    "Origen, recuperación y comprobación reducen riesgos.",
    {}
   ],
   [
    "choice",
    "¿De dónde conviene obtener una actualización?",
    [
     "Del canal oficial del sistema o aplicación",
     "De un enlace inesperado por chat",
     "De cualquier anuncio"
    ],
    "El canal oficial permite comprobar su procedencia.",
    {}
   ],
   [
    "choice",
    "¿Por qué preparar una copia antes de cambios relevantes?",
    [
     "Para poder recuperar datos si algo falla",
     "Para evitar todas las fallas posibles",
     "Para compartir datos públicamente"
    ],
    "Una copia ayuda a recuperar; no garantiza que nunca haya problemas.",
    {}
   ]
  ]
 },
 {
  "courseId": "digital-safety-v1",
  "id": "digital-respect",
  "title": "Convivencia y ayuda digital",
  "prerequisite": "digital-update",
  "module": "Usar tecnología con criterio",
  "explanation": "El respeto digital incluye cuidar privacidad, pedir consentimiento y buscar apoyo ante acoso. Conserva evidencia de un incidente sin difundirla públicamente y usa canales de ayuda adecuados.",
  "example": "Si alguien comparte una foto tuya sin permiso, pide apoyo a una persona de confianza y revisa cómo reportarla en la plataforma.",
  "alternative": "No respondas al acoso publicando datos personales de otra persona.",
  "items": [
   [
    "choice",
    "¿Qué haces antes de publicar una foto de un compañero?",
    [
     "Pedir su consentimiento",
     "Publicarla sin avisar",
     "Etiquetar su dirección"
    ],
    "Su privacidad y consentimiento importan.",
    {}
   ],
   [
    "order",
    "Ordena una búsqueda de ayuda ante acoso.",
    [
     "Conservar evidencia de forma privada",
     "Buscar una persona de confianza",
     "Reportar por canales adecuados"
    ],
    "Evita exponer más datos mientras buscas apoyo.",
    {}
   ],
   [
    "choice",
    "¿Qué respuesta protege mejor a la persona afectada?",
    [
     "Apoyarla y ayudarla a buscar ayuda",
     "Reenviar el contenido ofensivo",
     "Publicar sus datos para denunciar"
    ],
    "Reenviar contenido o datos puede aumentar el daño.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-states",
  "title": "Estados de la materia",
  "prerequisite": "science-evidence",
  "module": "Materia y energía",
  "explanation": "Sólidos, líquidos y gases tienen comportamientos diferentes. Un sólido mantiene forma; un líquido toma la del recipiente y conserva aproximadamente su volumen; un gas se expande para ocupar el espacio disponible.",
  "example": "El hielo es sólido, el agua líquida fluye y el vapor de agua es un gas.",
  "alternative": "Una piedra mantiene su forma; el agua de un vaso cambia de forma al verterla.",
  "items": [
   [
    "match",
    "Relaciona estado y propiedad.",
    [
     [
      "Sólido",
      "Mantiene forma"
     ],
     [
      "Líquido",
      "Fluye y toma forma del recipiente"
     ],
     [
      "Gas",
      "Se expande"
     ]
    ],
    "Los estados se distinguen por sus propiedades.",
    {}
   ],
   [
    "input",
    "El agua congelada se encuentra en estado ___.",
    [
     "solido",
     "liquido",
     "gaseoso"
    ],
    "El hielo es agua en estado sólido.",
    {}
   ],
   [
    "choice",
    "¿Qué pasa con un gas en un recipiente disponible?",
    [
     "Se expande para ocupar el espacio",
     "Siempre mantiene una forma propia",
     "Se convierte siempre en sólido"
    ],
    "Los gases se expanden; no tienen forma propia.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-changes",
  "title": "Cambios de estado",
  "prerequisite": "science-states",
  "module": "Materia y energía",
  "explanation": "Fusión es pasar de sólido a líquido; evaporación, de líquido a gas; condensación, de gas a líquido. Estos cambios pueden relacionarse con transferencia de energía.",
  "example": "El hielo que se derrite experimenta fusión. El agua que pasa a vapor se evapora.",
  "alternative": "Las gotas en una superficie fría pueden formarse por condensación del vapor del aire.",
  "items": [
   [
    "match",
    "Relaciona cambio y transformación.",
    [
     [
      "Fusión",
      "Sólido a líquido"
     ],
     [
      "Evaporación",
      "Líquido a gas"
     ],
     [
      "Condensación",
      "Gas a líquido"
     ]
    ],
    "Los nombres dependen del estado inicial y final.",
    {}
   ],
   [
    "choice",
    "El hielo se derrite. ¿Qué cambio ocurre?",
    [
     "Fusión",
     "Condensación",
     "Congelación"
    ],
    "Pasa de sólido a líquido: fusión.",
    {}
   ],
   [
    "choice",
    "Vapor forma gotas sobre una superficie fría. ¿Qué cambio ocurre?",
    [
     "Condensación",
     "Fusión",
     "Evaporación"
    ],
    "El gas pasa a líquido.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-energy",
  "title": "Transformaciones de energía",
  "prerequisite": "science-changes",
  "module": "Materia y energía",
  "explanation": "La energía puede transferirse y transformarse. Un dispositivo puede convertir energía eléctrica en luz, movimiento y calor; no toda la energía termina en el efecto deseado.",
  "example": "Una lámpara transforma energía eléctrica en luz y también en calor.",
  "alternative": "Un ventilador convierte energía eléctrica en movimiento y parte en calor y sonido.",
  "items": [
   [
    "match",
    "Relaciona dispositivo y efecto principal.",
    [
     [
      "Lámpara",
      "Luz"
     ],
     [
      "Ventilador",
      "Movimiento"
     ],
     [
      "Calefactor",
      "Calor"
     ]
    ],
    "Cada dispositivo transforma energía en distintos efectos.",
    {}
   ],
   [
    "choice",
    "Además de luz, una lámpara puede producir…",
    [
     "Calor",
     "Nada de energía",
     "Agua necesariamente"
    ],
    "Parte de la energía eléctrica se transforma en calor.",
    {}
   ],
   [
    "choice",
    "¿Qué describe mejor un ventilador funcionando?",
    [
     "Transforma energía eléctrica en movimiento y otros efectos",
     "Crea energía de la nada",
     "Destruye toda la energía"
    ],
    "La energía se transforma y transfiere.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-force",
  "title": "Fuerzas y movimiento",
  "prerequisite": "science-energy",
  "module": "Materia y energía",
  "explanation": "Una fuerza es una interacción que puede cambiar el movimiento o deformar un objeto. Empujar y tirar son ejemplos; el resultado depende de las fuerzas que actúan y del objeto.",
  "example": "Empujar un carrito puede aumentar su velocidad; el rozamiento se opone al deslizamiento.",
  "alternative": "Al apretar una esponja, una fuerza cambia su forma.",
  "items": [
   [
    "match",
    "Relaciona interacción y efecto posible.",
    [
     [
      "Empujar un carrito",
      "Cambiar su movimiento"
     ],
     [
      "Apretar una esponja",
      "Deformar"
     ],
     [
      "Rozamiento",
      "Oponerse al deslizamiento"
     ]
    ],
    "Las fuerzas pueden afectar movimiento y forma.",
    {}
   ],
   [
    "choice",
    "¿Qué muestra una deformación por fuerza?",
    [
     "Apretar una esponja",
     "Mirar un dibujo",
     "Cambiar el nombre de un objeto"
    ],
    "Apretar produce una interacción que modifica la forma.",
    {}
   ],
   [
    "choice",
    "Un carrito se frena al deslizarse. ¿Qué fuerza suele contribuir?",
    [
     "Rozamiento",
     "Un nombre más largo",
     "Una nueva temperatura siempre"
    ],
    "El rozamiento puede oponerse al movimiento relativo.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-cells",
  "title": "Células y seres vivos",
  "prerequisite": "science-evidence",
  "module": "Vida y ambiente",
  "explanation": "La célula es una unidad básica de los seres vivos. Algunos organismos tienen una sola célula; otros tienen muchas. No todas las células tienen las mismas estructuras.",
  "example": "Una bacteria es un organismo unicelular. Un árbol tiene muchas células organizadas en tejidos.",
  "alternative": "Las células vegetales tienen pared celular; muchas poseen cloroplastos para realizar fotosíntesis.",
  "items": [
   [
    "match",
    "Relaciona concepto y descripción.",
    [
     [
      "Unicelular",
      "Una célula"
     ],
     [
      "Multicelular",
      "Muchas células"
     ],
     [
      "Tejido",
      "Conjunto organizado de células"
     ]
    ],
    "La organización puede pasar de células a tejidos.",
    {}
   ],
   [
    "input",
    "Un organismo de una sola célula es ___.",
    [
     "unicelular",
     "multicelular",
     "invisible"
    ],
    "Unicelular significa formado por una célula.",
    {}
   ],
   [
    "choice",
    "¿Cuál afirmación es correcta?",
    [
     "Los seres vivos pueden tener una o muchas células",
     "Todos tienen una sola célula",
     "Todas las células son idénticas"
    ],
    "Hay diversidad de organismos y células.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-food",
  "title": "Cadenas alimentarias",
  "prerequisite": "science-cells",
  "module": "Vida y ambiente",
  "explanation": "Una cadena alimentaria representa relaciones de alimentación y transferencia de energía. En el esquema productor → consumidor, la flecha apunta hacia quien recibe alimento y energía.",
  "example": "Hierba → conejo → zorro. La hierba es productora; el conejo y el zorro son consumidores.",
  "alternative": "Algas → pez pequeño → pez grande muestra otra cadena posible.",
  "items": [
   [
    "order",
    "Ordena esta cadena desde el productor.",
    [
     "Hierba",
     "Conejo",
     "Zorro"
    ],
    "El conejo come hierba y el zorro puede alimentarse del conejo.",
    {}
   ],
   [
    "choice",
    "En hierba → conejo → zorro, ¿quién es productor?",
    [
     "Hierba",
     "Conejo",
     "Zorro"
    ],
    "La hierba produce materia orgánica mediante fotosíntesis.",
    {}
   ],
   [
    "choice",
    "¿Qué representa la flecha en esta cadena?",
    [
     "Transferencia de alimento y energía hacia el consumidor",
     "Quién corre más rápido",
     "Una jerarquía de inteligencia"
    ],
    "La flecha va hacia quien recibe energía al alimentarse.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-water",
  "title": "Ciclo del agua",
  "prerequisite": "science-food",
  "module": "Vida y ambiente",
  "explanation": "El agua circula mediante evaporación, condensación, precipitación y otros procesos. Después puede infiltrarse en el suelo o escurrir hacia ríos y mares.",
  "example": "El agua se evapora, el vapor se condensa en gotas y puede caer como lluvia.",
  "alternative": "El agua de lluvia puede entrar en el suelo; no toda vuelve al río por la superficie.",
  "items": [
   [
    "order",
    "Ordena estos procesos de un recorrido del agua.",
    [
     "Evaporación",
     "Condensación",
     "Precipitación"
    ],
    "Es un recorrido posible del ciclo; luego continúan otros procesos.",
    {}
   ],
   [
    "match",
    "Relaciona proceso y descripción.",
    [
     [
      "Precipitación",
      "Caída de agua desde nubes"
     ],
     [
      "Infiltración",
      "Entrada al suelo"
     ],
     [
      "Escorrentía",
      "Flujo sobre la superficie"
     ]
    ],
    "El agua puede seguir caminos distintos después de caer.",
    {}
   ],
   [
    "choice",
    "¿Qué ocurre cuando el vapor forma gotas?",
    [
     "Condensación",
     "Infiltración",
     "Escorrentía"
    ],
    "La condensación transforma vapor en líquido.",
    {}
   ]
  ]
 },
 {
  "courseId": "science-v1",
  "id": "science-evidence-life",
  "title": "Decisiones ambientales con evidencia",
  "prerequisite": "science-water",
  "module": "Vida y ambiente",
  "explanation": "Para evaluar una medida ambiental, define qué quieres mejorar y cómo lo medirás. Compara datos en condiciones pertinentes y reconoce otros factores que pudieron cambiar.",
  "example": "Para estudiar ahorro de agua, registra consumo antes y después y considera cuántas personas estuvieron presentes.",
  "alternative": "Menos consumo un día no demuestra por sí solo que una medida funciona siempre.",
  "items": [
   [
    "order",
    "Ordena una evaluación de ahorro de agua.",
    [
     "Definir medida y forma de registrar",
     "Comparar datos antes y después",
     "Revisar factores y límites"
    ],
    "La comparación necesita contexto, no solo dos números.",
    {}
   ],
   [
    "choice",
    "El consumo bajó, pero hubo menos personas. ¿Qué reconoces?",
    [
     "La cantidad de personas pudo influir",
     "La medida quedó probada sin límites",
     "Los datos no importan"
    ],
    "Un factor adicional puede explicar parte de la diferencia.",
    {}
   ],
   [
    "choice",
    "¿Qué fortalece una conclusión?",
    [
     "Más registros comparables y reconocimiento de límites",
     "Ocultar los días que no apoyan la idea",
     "Elegir solo el mejor resultado"
    ],
    "Una evaluación fiable incluye evidencia pertinente y límites.",
    {}
   ]
  ]
 }
];
