# 📋 Instructions for Adding New Columns to Diary Table

**When you need to add a new column to the diary table:**

## 1. **Add the column to the table definition** (around line 20)
```sql
-- Additional useful diary fields
title VARCHAR(255) NOT NULL,
content TEXT,
revised_content TEXT,
your_new_column_name DATA_TYPE,  ← ADD HERE
mood VARCHAR(50),
```

## 2. **Add the ALTER TABLE statement** (around line 30)
```sql
-- Add new columns to existing table (for development updates)
ALTER TABLE diary ADD COLUMN IF NOT EXISTS revised_content TEXT;
ALTER TABLE diary ADD COLUMN IF NOT EXISTS your_new_column_name DATA_TYPE;  ← ADD HERE
```

## 3. **Add documentation comment** (around line 55)
```sql
COMMENT ON COLUMN diary.content IS 'Main content/body of the diary entry';
COMMENT ON COLUMN diary.revised_content IS 'Revised or edited version of the diary content';
COMMENT ON COLUMN diary.your_new_column_name IS 'Description of what this column stores';  ← ADD HERE
```

## 4. **Common data types to use:**
- `VARCHAR(255)` - Short text (titles, names)
- `TEXT` - Long text (descriptions, content)
- `INTEGER` - Numbers (counts, IDs)
- `BOOLEAN` - True/false values
- `TIMESTAMP WITH TIME ZONE` - Dates/times
- `TEXT[]` - Arrays of text (tags)

## 5. **Test the script:**
- Run the script to make sure it works
- Check that existing data is preserved
- Verify the new column appears in your database

**Remember:** Always use `IF NOT EXISTS` so the script can be run multiple times safely!

---

## Example: Adding a "word_count" column

### Step 1: Add to table definition
```sql
title VARCHAR(255) NOT NULL,
content TEXT,
revised_content TEXT,
word_count INTEGER,  ← NEW COLUMN
mood VARCHAR(50),
```

### Step 2: Add ALTER TABLE statement
```sql
ALTER TABLE diary ADD COLUMN IF NOT EXISTS word_count INTEGER;
```

### Step 3: Add comment
```sql
COMMENT ON COLUMN diary.word_count IS 'Number of words in the diary entry';
```

---

**This file should be updated whenever new patterns or requirements are discovered during development.**
