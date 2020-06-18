from app.Cloud import Cloud

def test_getDefaulttBucketName():
    c = Cloud()
    assert c.getDefaulttBucketName() == 'xttest71af37fb-e935-43cc-994e-fdf320a72059'