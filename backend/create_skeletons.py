import os

# Empty init files
inits = [
    r'D:\Hydroponics\backend\app\routes\__init__.py',
    r'D:\Hydroponics\backend\app\models\__init__.py',
    r'D:\Hydroponics\backend\app\services\__init__.py',
    r'D:\Hydroponics\backend\app\utils\__init__.py',
    r'D:\Hydroponics\backend\app\ml\__init__.py',
    r'D:\Hydroponics\backend\app\ml\preprocessing\__init__.py',
    r'D:\Hydroponics\backend\app\ml\training\__init__.py',
    r'D:\Hydroponics\backend\app\ml\inference\__init__.py',
    r'D:\Hydroponics\backend\app\ml\explainability\__init__.py',
    r'D:\Hydroponics\backend\tests\__init__.py',
]
for p in inits:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').close()
    print('Created', p)

# Blueprint skeletons
blueprints = [
    'auth', 'user', 'buyer', 'admin', 'location', 'weather',
    'cultivation', 'recommendation', 'economics', 'quality',
    'laboratory', 'market', 'matching', 'planning',
]
for name in blueprints:
    path = os.path.join(r'D:\Hydroponics\backend\app\routes', name + '.py')
    content = 'from flask import Blueprint\n' + name + '_bp = Blueprint("' + name + '", __name__)\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Created', path)

print('All done.')
