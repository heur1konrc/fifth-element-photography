# Lumaprints API Field Names

**CRITICAL**: Lumaprints uses different field names than expected!

## Field Mapping

| Object Type | ID Field Name | Example Value |
|-------------|---------------|---------------|
| Category | `id` | 3 |
| Subcategory | `subcategoryId` | 101002 |
| Options | (TBD) | (TBD) |

## Example Responses

### Category
```json
{
  "id": 3,
  "name": "Framed Canvas"
}
```

### Subcategory
```json
{
  "subcategoryId": 101002,
  "name": "1.25in Framed Canvas",
  "minimumWidth": 5,
  "maximumWidth": 120,
  "minimumHeight": 5,
  "maximumHeight": 52,
  "requiredDPI": 200
}
```

## Code Usage

```javascript
// ✅ CORRECT
const categoryId = state.selectedCategory.id;
const subcategoryId = state.selectedSubcategory.subcategoryId;

// ❌ WRONG
const subcategoryId = state.selectedSubcategory.id; // undefined!
```

## API Documentation
- Categories: https://api-docs.lumaprints.com/api-5384562
- Subcategories: https://api-docs.lumaprints.com/api-5384563
- Options: https://api-docs.lumaprints.com/api-5384564

