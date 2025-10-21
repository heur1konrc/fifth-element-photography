-- Fix Framed Fine Art products that are miscategorized
-- Move products from "Canvas - Rolled" category to correct Framed Fine Art categories

-- Update 0.875" frame products (lumaprints_subcategory_id 105001-105003)
UPDATE products 
SET category_id = 15  -- "Framed Fine Art - 0.875" Frame"
WHERE product_type_id = 4 
  AND lumaprints_subcategory_id IN (105001, 105002, 105003)
  AND category_id != 15;

-- Update 1.25" frame products (lumaprints_subcategory_id 105005-105007)
UPDATE products 
SET category_id = 16  -- "Framed Fine Art - 1.25" Frame"
WHERE product_type_id = 4 
  AND lumaprints_subcategory_id IN (105005, 105006, 105007)
  AND category_id != 16;

-- Verify the fix
SELECT 'After fix:' as status;
SELECT c.name, COUNT(*) as count 
FROM products p 
JOIN categories c ON p.category_id = c.id 
WHERE p.product_type_id = 4 AND p.active = 1 
GROUP BY c.name;

