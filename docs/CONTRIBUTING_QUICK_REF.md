# MarkItDown Contributor Quick Reference

## Setup

```bash
git clone https://github.com/microsoft/markitdown.git
cd markitdown
pip install -e "packages/markitdown[dev]"
```

## Running tests

```bash
pytest packages/markitdown/tests/ -v
```

## Adding a new converter

1. Create a class that inherits from `DocumentConverter`.
2. Implement `convert(local_path, **kwargs) -> DocumentConverterResult | None`.
3. Return `None` when the converter cannot handle the file type.
4. Register via `MarkItDown.register_converter(MyConverter())`.
5. Add tests in `packages/markitdown/tests/`.
6. Update the supported formats table in `README.md`.

## Converter checklist

- [ ] Returns `None` for unsupported extensions (not raises).
- [ ] Produces clean Markdown without HTML tags.
- [ ] `DocumentConverterResult.title` is set when a document title is
  available.
- [ ] Extra dependencies are optional and guarded with `try/except ImportError`.
- [ ] Unit test covers at least: a valid file, an unsupported extension.

## Testing with sample files

```bash
python -c "
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert('samples/test.pdf')
print(result.text_content[:500])
"
```
