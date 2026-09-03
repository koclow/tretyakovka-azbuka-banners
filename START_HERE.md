# Баннеры Третьяковка × Азбука вкуса

Два HTML-баннера из макета Figma «РБК третьяковка х азбука (Copy)»: 680×250 и
300×250, фиксированные размеры, лёгкая CSS-анимация. Плюс витрина на тёмном
фоне, опубликованная через GitHub Pages.

* Живая страница — <https://koclow.github.io/tretyakovka-azbuka-banners/>
* Репозиторий — <https://github.com/koclow/tretyakovka-azbuka-banners> (публичный: Pages на бесплатном плане иначе не работает)
* Макет — <https://www.figma.com/design/SbssgqdMl8toWJz8wyqC4d/?node-id=1-2>

## Что где

| Путь | Что |
|---|---|
| `index.html` | витрина: оба баннера в iframe на тёмном фоне |
| `banners/680x250/` | горизонтальный баннер + слои в `assets/` |
| `banners/300x250/` | квадратный баннер + слои в `assets/` |
| `dist/` | те же баннеры одиночными файлами (картинки внутри как data:URI) |
| `build-standalone.py` | сборка `dist/` |
| `README.md` | как устроены слои и анимация, почему тексты растром |

## Как работать

Папка — сама себе git-репозиторий, `origin` = GitHub. Правки в `main` уезжают
на Pages автоматически, минута-две на сборку. После правки баннера пересобрать
одиночные файлы: `python3 build-standalone.py`.

Состояние — `PROJECT_STATUS.md`.
