USE `db_dispenda`;

-- 1. Find orphaned id_tagihan in tb_pembayaran
SELECT 'Orphaned pembayaran rows:' AS info;
SELECT p.id_pembayaran, p.id_tagihan
FROM tb_pembayaran p
LEFT JOIN tb_tagihan t ON p.id_tagihan = t.id_tagihan
WHERE t.id_tagihan IS NULL;

-- 2. Get first valid id_tagihan to use as fallback
SET @valid_tagihan = (SELECT MIN(id_tagihan) FROM tb_tagihan);
SELECT CONCAT('Using fallback id_tagihan: ', @valid_tagihan) AS info;

-- 3. Update orphaned rows to reference valid id_tagihan
UPDATE tb_pembayaran p
LEFT JOIN tb_tagihan t ON p.id_tagihan = t.id_tagihan
SET p.id_tagihan = @valid_tagihan
WHERE t.id_tagihan IS NULL;

-- 4. Verify no more orphans
SELECT 'Remaining orphans after fix:' AS info;
SELECT COUNT(*) AS orphan_count
FROM tb_pembayaran p
LEFT JOIN tb_tagihan t ON p.id_tagihan = t.id_tagihan
WHERE t.id_tagihan IS NULL;

-- 5. Add new constraint (no old constraint to drop - result set was empty)
ALTER TABLE tb_pembayaran
ADD CONSTRAINT fk_pembayaran_tagihan
FOREIGN KEY (id_tagihan) REFERENCES tb_tagihan(id_tagihan)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 7. Verify new constraint
SELECT 'New constraint created:' AS info;
SHOW CREATE TABLE tb_pembayaran\G