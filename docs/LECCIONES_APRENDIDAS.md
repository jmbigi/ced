# Lecciones Aprendidas

Errores cometidos durante el desarrollo de este proyecto y cómo evitarlos.

## 1. No creer al usuario cuando reporta un bug

**Error:** El usuario dijo "no se puede escribir en el editor". Revisé el
código y mis tests pasaban, así que asumí que el usuario estaba
equivocado. Pasé horas buscando bugs inexistentes en los tests cuando el
bug real era en la aplicación.

**Lección:** El usuario siempre tiene razón. Si dice que algo no funciona,
es porque no funciona, independientemente de lo que digan los tests.

## 2. No probar la aplicación real

**Error:** Ejecuté cientos de tests automatizados pero nunca ejecuté el
comando `ced` en la terminal para probar manualmente. Los tests unitarios
no capturan problemas de runtime como `AttributeError: confirm` o bugs de
layout que solo se ven en ejecución real.

**Lección:** Siempre probar la aplicación real antes de declarar un
bug como resuelto. Los tests son complemento, no reemplazo.

## 3. Asumir que `App.confirm()` existe en Textual 8.x

**Error:** Un commit mencionaba "usar built-in App.confirm()". Asumí
que existía sin verificarlo. Textual 8.2.7 no tiene `App.confirm()`.
El resultado: `AttributeError` al cerrar pestañas.

**Lección:** Siempre verificar que una API existe en la versión instalada
antes de usarla: `python3 -c "from textual.app import App; App.confirm"`.

## 4. Cambiar el código sin entender la causa raíz

**Error:** Cambié `self.confirm()` por `push_screen(ConfirmScreen)`
con `await` y `wait_for_dismiss=True`, pero eso requiere un worker
de Textual. Luego lo cambié a patrón callback sin entender por qué
fallaba el await.

**Lección:** Entender la causa raíz completa antes de aplicar un fix.
Probar el fix en la app real, no solo en tests.

## 5. Ignorar el foco inicial de los widgets

**Error:** Los tests de PTY write enviaban texto al stdin de ced,
asumiendo que iría al editor. El foco inicial está en el file tree,
por lo que todo el texto aparecía en el panel izquierdo. Afirmé en el
commit que "Hola mundo está en el editor" cuando en realidad estaba en
el file tree.

**Lección:** Conocer el estado inicial de la aplicación (foco, widgets
activos) antes de diseñar la interacción del test.

## 6. No verificar el layout en diferentes tamaños de terminal

**Error:** El `ContentSwitcher` dentro de `TabbedContent` medía 2 líneas
en vez de 37. El layout se veía bien en tests pequeños pero el editor
era inusable. No lo detecté porque nunca ejecuté `ced` en una terminal
real de 120x40.

**Lección:** Probar el layout en múltiples tamaños de terminal. Un
widget con `height: 100%` no siempre funciona si su contenedor no
propaga la altura correctamente.

## 7. Tests frágiles que dependen de OCR para texto pequeño

**Error:** Usar Tesseract OCR para verificar texto en una terminal
de fuente 12px. Tesseract no lee texto tan pequeño de forma confiable.
Los tests fallaban intermitentemente y atribuí el error a "font size
too small for Tesseract" en vez de rediseñar el enfoque de test.

**Lección:** Usar la API interna del framework (Textual) para verificar
contenido (p. ej., `editor.text`). OCR es para verificación visual
cualitativa, no para aserciones precisas.

## 8. No verificar el estado del Input cuando tiene foco

**Error:** El Input de OpenCode tenía `color: $text` heredado, pero
al recibir foco, el estilo podía cambiar. No verifiqué que el texto
fuera visible con el Input enfocado.

**Lección:** Verificar el rendering del widget en todos sus estados
(foco, hover, disabled, etc.). Un widget puede verse bien sin foco
pero mal con foco, o viceversa.

## 9. Commitear cambios sin probar en la app real

**Error:** Varios commits corrigieron bugs que solo existían en mi
cabeza porque los tests pasaban pero nunca ejecuté la app. Ejemplo:
el fix del layout del editor (ContentSwitcher height) solo se notó
cuando el usuario reportó que no podía escribir.

**Lección:** Antes de cada commit: (1) ejecutar tests, (2) ejecutar
la app real, (3) probar la funcionalidad modificada manualmente.

## 10. Ignorar las advertencias del usuario sobre mi terquedad

**Error:** El usuario me dijo repetidamente "estás escribiendo en
cualquier lado", "revisa bien", "te quedaste atascado". Ignoré estas
señales y seguí insistiendo en mi versión incorrecta.

**Lección:** Cuando el usuario dice que algo está mal, dejar de
defender el código actual y ponerse a investigar desde cero.

## Checklist pre-commit

Antes de hacer commit, verificar:

- [ ] `pytest tests/ -q` — todos los tests pasan
- [ ] `ced` arranca sin errores
- [ ] Se puede escribir en el editor (Ctrl+N, teclear)
- [ ] Se pueden abrir archivos desde el sidebar
- [ ] Cerrar pestañas funciona (con y sin modificaciones)
- [ ] El layout se ve bien en 120x40
- [ ] El Input de OpenCode muestra el texto mientras se escribe
- [ ] No hay `print()` ni `pdb` olvidados en el código
