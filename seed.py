import os
import django

# Set up django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from shop.models import Product, Order, OrderItem, CartItem

def seed_db():
    print("Resetting database state and seeding with INR values...")
    
    # Clean up existing data
    Order.objects.all().delete()
    OrderItem.objects.all().delete()
    CartItem.objects.all().delete()
    Product.objects.all().delete()
    
    products = [
        {
            'name': 'ZenBuds Pro',
            'price': 12499.00,
            'description': 'Experience pure sound with active noise cancellation (ANC), custom drivers, and up to 30 hours of wireless playtime. Packed in a clean charging case.',
            'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop',
            'stock': 15
        },
        {
            'name': 'Aura Keyboard',
            'price': 9999.00,
            'description': 'A clean 75% mechanical keyboard featuring tactile brown switches, double-shot keycaps, and multi-mode wireless/wired connectivity for daily typing.',
            'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&auto=format&fit=crop',
            'stock': 8
        },
        {
            'name': 'Nova Charger',
            'price': 5999.00,
            'description': 'A minimal aluminum 3-in-1 magnetic wireless charging stand. Power up your smartphone, smartwatch, and wireless earbuds simultaneously on your desk.',
            'image_url': 'https://images.unsplash.com/photo-1622445262465-2481c8575326?w=500&auto=format&fit=crop',
            'stock': 25
        },
        {
            'name': 'Holo Frame',
            'price': 14999.00,
            'description': 'A clean smart desk display showing calendar widgets, digital time, and weather indicators. Fits perfectly on any office work desk setup.',
            'image_url': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop',
            'stock': 5
        },
        {
            'name': 'Apex Mouse',
            'price': 6999.00,
            'description': 'An ergonomic and lightweight optical wireless mouse. Features precise tracking, long battery life, and a clean minimalist design for office and gaming.',
            'image_url': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&auto=format&fit=crop',
            'stock': 12
        },
        {
            'name': 'Vivid Screen',
            'price': 39999.00,
            'description': 'A clean 34-inch curved monitor display. Experience crisp visuals and fluid responsiveness for multi-tasking, writing code, and editing media.',
            'image_url': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&auto=format&fit=crop',
            'stock': 6
        }
    ]

    for p in products:
        product = Product.objects.create(**p)
        print(f"Created product: {product.name}")
        
    print("Database seeding completed successfully with INR values!")

if __name__ == '__main__':
    seed_db()
