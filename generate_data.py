"""
ShopIndia E-commerce Analytics
Author: Mehak Pandey | pandeymehak.217@gmail.com
Dataset: 6 tables | 40,000 orders | 2020-2024
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(17)
np.random.seed(17)

BASE = '/home/claude/ecommerce_project/data'

STATES = ['Maharashtra','Karnataka','Delhi','Tamil Nadu','Telangana',
          'Gujarat','Rajasthan','West Bengal','Uttar Pradesh','Kerala',
          'Punjab','Haryana','Madhya Pradesh','Bihar','Andhra Pradesh']

CITIES = {
    'Maharashtra':  ['Mumbai','Pune','Nagpur','Thane','Nashik'],
    'Karnataka':    ['Bengaluru','Mysuru','Hubli','Mangaluru','Belgaum'],
    'Delhi':        ['New Delhi','Noida','Gurgaon','Faridabad','Ghaziabad'],
    'Tamil Nadu':   ['Chennai','Coimbatore','Madurai','Salem','Trichy'],
    'Telangana':    ['Hyderabad','Warangal','Karimnagar','Nizamabad','Khammam'],
    'Gujarat':      ['Ahmedabad','Surat','Vadodara','Rajkot','Gandhinagar'],
    'Rajasthan':    ['Jaipur','Jodhpur','Udaipur','Kota','Ajmer'],
    'West Bengal':  ['Kolkata','Howrah','Durgapur','Siliguri','Asansol'],
    'Uttar Pradesh':['Lucknow','Kanpur','Agra','Varanasi','Allahabad'],
    'Kerala':       ['Kochi','Thiruvananthapuram','Kozhikode','Thrissur','Kollam'],
    'Punjab':       ['Chandigarh','Ludhiana','Amritsar','Jalandhar','Patiala'],
    'Haryana':      ['Gurugram','Faridabad','Hisar','Rohtak','Panipat'],
    'Madhya Pradesh':['Bhopal','Indore','Gwalior','Jabalpur','Ujjain'],
    'Bihar':        ['Patna','Gaya','Muzaffarpur','Bhagalpur','Darbhanga'],
    'Andhra Pradesh':['Vijayawada','Visakhapatnam','Guntur','Tirupati','Nellore'],
}

CATEGORIES = ['Electronics','Fashion','Home & Kitchen','Books',
              'Sports & Fitness','Beauty & Health','Toys & Games',
              'Grocery','Automotive','Office Supplies']

SUBCATEGORIES = {
    'Electronics':    ['Mobile Phones','Laptops','Tablets','Headphones','Cameras','Smart Watches','TV & Monitors'],
    'Fashion':        ['Men Clothing','Women Clothing','Footwear','Bags & Wallets','Sunglasses','Jewellery'],
    'Home & Kitchen': ['Cookware','Furniture','Bedding','Cleaning','Storage','Lighting','Decor'],
    'Books':          ['Fiction','Non-Fiction','Academic','Children','Self-Help','Business'],
    'Sports & Fitness':['Gym Equipment','Cricket','Football','Yoga','Cycling','Swimming'],
    'Beauty & Health': ['Skincare','Haircare','Makeup','Supplements','Medical Devices'],
    'Toys & Games':   ['Board Games','Action Figures','Educational','Outdoor','Electronic Toys'],
    'Grocery':        ['Snacks','Beverages','Staples','Dairy','Organic','Spices'],
    'Automotive':     ['Car Accessories','Bike Accessories','Tools','Oils & Fluids','Tyres'],
    'Office Supplies':['Stationery','Printers','Furniture','Storage','Whiteboards'],
}

BRANDS = {
    'Electronics':    ['Samsung','Apple','OnePlus','Xiaomi','Sony','LG','Boat','Realme'],
    'Fashion':        ['Zara','H&M','Fabindia','Peter England','Bata','Nike','Adidas','Puma'],
    'Home & Kitchen': ['Prestige','Hawkins','Godrej','Nilkamal','Asian Paints','Philips'],
    'Books':          ['Penguin','HarperCollins','Oxford','S.Chand','Scholastic','Rupa'],
    'Sports & Fitness':['Decathlon','Nivia','SG','Cosco','Yonex','Reebok'],
    'Beauty & Health': ['Lakme','Mamaearth','Himalaya','Patanjali','LOreal','Biotique'],
    'Toys & Games':   ['Funskool','Lego','Hasbro','Fisher-Price','Mattel','Toyzone'],
    'Grocery':        ['Aashirvaad','Amul','Nestle','Britannia','Dabur','Haldirams'],
    'Automotive':     ['Bosch','3M','Meguiars','Castrol','MRF','CEAT'],
    'Office Supplies':['Classmate','Faber-Castell','HP','Canon','Godrej','Nilkamal'],
}

PAYMENT_METHODS = ['Credit Card','Debit Card','UPI','Net Banking',
                   'Cash on Delivery','EMI','Wallet']
PAY_WEIGHTS     = [22,18,30,8,12,6,4]

SHIPPING_TYPES  = ['Standard','Express','Same Day','Free Shipping']
SHIP_WEIGHTS    = [40,25,5,30]

ORDER_STATUS    = ['Delivered','Returned','Cancelled','Pending']
STATUS_WEIGHTS  = [78,10,8,4]

RETURN_REASONS  = ['Defective Product','Wrong Item','Size Issue',
                   'Better Price Found','Changed Mind','Damaged in Transit']

first_names = ['Aarav','Aditi','Aditya','Akash','Ananya','Anjali','Arjun',
               'Deepika','Divya','Ishaan','Isha','Karan','Kavya','Meera',
               'Mihir','Nisha','Priya','Rahul','Riya','Rohit','Sanjay',
               'Shreya','Siddharth','Sneha','Tanvi','Utkarsh','Varun',
               'Vikram','Yash','Amit','Pooja','Rajesh','Sunita','Manoj']

last_names = ['Sharma','Patel','Singh','Gupta','Kumar','Verma','Joshi',
              'Nair','Reddy','Mehta','Shah','Iyer','Pillai','Rao',
              'Malhotra','Agarwal','Banerjee','Mishra','Pandey','Trivedi']

def rand_date(s, e):
    s = datetime.strptime(s, '%Y-%m-%d')
    e = datetime.strptime(e, '%Y-%m-%d')
    return s + timedelta(seconds=random.randint(0, int((e-s).total_seconds())))

# ── TABLE 1: CUSTOMERS ─────────────────────────────────────
N_CUSTOMERS = 5000
customers = []
for cid in range(1, N_CUSTOMERS+1):
    state = random.choice(STATES)
    city  = random.choice(CITIES[state])
    reg   = rand_date('2018-01-01','2023-12-31')
    age   = random.randint(18, 60)
    income_bracket = random.choices(
        ['<3L','3-6L','6-10L','10-20L','>20L'],
        weights=[20,30,25,15,10])[0]
    customers.append({
        'customer_id':       f'CUST{cid:05d}',
        'customer_name':     f'{random.choice(first_names)} {random.choice(last_names)}',
        'email':             f'user{cid}@email.com',
        'age':               age,
        'gender':            random.choices(['Male','Female','Other'],weights=[52,46,2])[0],
        'state':             state,
        'city':              city,
        'pincode':           random.randint(100000,999999),
        'registration_date': reg.strftime('%Y-%m-%d'),
        'income_bracket':    income_bracket,
        'customer_type':     random.choices(['New','Regular','Premium','VIP'],
                                            weights=[20,45,25,10])[0],
        'is_prime_member':   random.choices([1,0],weights=[35,65])[0],
        'preferred_category':random.choice(CATEGORIES),
        'acquisition_source':random.choices(
            ['Organic Search','Social Media','Email Campaign',
             'Referral','Paid Ads','App Store'],
            weights=[25,20,15,20,15,5])[0],
    })
customers_df = pd.DataFrame(customers)

# ── TABLE 2: PRODUCTS ──────────────────────────────────────
N_PRODUCTS = 800
products = []
for pid in range(1, N_PRODUCTS+1):
    cat    = random.choice(CATEGORIES)
    subcat = random.choice(SUBCATEGORIES[cat])
    brand  = random.choice(BRANDS[cat])
    price_map = {
        'Electronics':    (500,  150000),
        'Fashion':        (200,  15000),
        'Home & Kitchen': (150,  50000),
        'Books':          (100,  2000),
        'Sports & Fitness':(200, 30000),
        'Beauty & Health': (100, 5000),
        'Toys & Games':   (200,  8000),
        'Grocery':        (50,   2000),
        'Automotive':     (100,  20000),
        'Office Supplies': (50,  10000),
    }
    lo, hi = price_map[cat]
    mrp    = round(random.uniform(lo, hi), 0)
    discount_pct = random.choice([0,5,10,15,20,25,30,40,50])
    selling_price= round(mrp * (1-discount_pct/100), 0)
    products.append({
        'product_id':     f'PROD{pid:04d}',
        'product_name':   f'{brand} {subcat} {random.randint(100,999)}',
        'category':       cat,
        'subcategory':    subcat,
        'brand':          brand,
        'mrp':            mrp,
        'selling_price':  selling_price,
        'discount_pct':   discount_pct,
        'cost_price':     round(selling_price * random.uniform(0.4, 0.7), 0),
        'weight_kg':      round(random.uniform(0.1, 15.0), 2),
        'rating':         round(random.uniform(2.5, 5.0), 1),
        'review_count':   random.randint(0, 5000),
        'stock_quantity': random.randint(0, 500),
        'is_active':      random.choices([1,0],weights=[92,8])[0],
        'launch_date':    rand_date('2018-01-01','2023-01-01').strftime('%Y-%m-%d'),
        'supplier_id':    f'SUP{random.randint(1,50):03d}',
    })
products_df = pd.DataFrame(products)

# ── TABLE 3: ORDERS ────────────────────────────────────────
N_ORDERS = 40000
orders = []
for oid in range(1, N_ORDERS+1):
    cust     = customers_df.sample(1).iloc[0]
    order_dt = rand_date('2020-01-01','2024-12-31')
    status   = random.choices(ORDER_STATUS, weights=STATUS_WEIGHTS)[0]
    ship_type= random.choices(SHIPPING_TYPES, weights=SHIP_WEIGHTS)[0]
    payment  = random.choices(PAYMENT_METHODS, weights=PAY_WEIGHTS)[0]

    ship_days = {'Standard':5,'Express':2,'Same Day':1,'Free Shipping':7}[ship_type]
    delivery_dt = order_dt + timedelta(days=ship_days+random.randint(0,3))

    ship_charge = {'Standard':49,'Express':99,'Same Day':199,'Free Shipping':0}[ship_type]

    orders.append({
        'order_id':          f'ORD{oid:07d}',
        'customer_id':       cust['customer_id'],
        'order_date':        order_dt.strftime('%Y-%m-%d'),
        'order_month':       order_dt.strftime('%Y-%m'),
        'order_year':        order_dt.year,
        'order_quarter':     f'Q{(order_dt.month-1)//3+1}',
        'order_day_of_week': order_dt.strftime('%A'),
        'order_hour':        order_dt.hour,
        'order_status':      status,
        'payment_method':    payment,
        'shipping_type':     ship_type,
        'shipping_charge':   ship_charge,
        'delivery_date':     delivery_dt.strftime('%Y-%m-%d') if status=='Delivered' else None,
        'delivery_days':     ship_days + random.randint(0,3) if status=='Delivered' else None,
        'state':             cust['state'],
        'city':              cust['city'],
        'is_prime_order':    cust['is_prime_member'],
        'coupon_applied':    random.choices([1,0],weights=[30,70])[0],
        'coupon_code':       random.choice(['SAVE10','FLAT20','NEW15','PRIME30',None,None,None]),
    })
orders_df = pd.DataFrame(orders)

# ── TABLE 4: ORDER ITEMS ───────────────────────────────────
order_items = []
item_id = 1
for _, order in orders_df.iterrows():
    n_items = random.choices([1,2,3,4,5],weights=[50,25,12,8,5])[0]
    used    = []
    for _ in range(n_items):
        prod = products_df[~products_df['product_id'].isin(used)].sample(1).iloc[0]
        used.append(prod['product_id'])
        qty  = random.choices([1,2,3,4],weights=[60,25,10,5])[0]
        disc = prod['discount_pct'] + random.choice([0,0,0,5,10])
        disc = min(disc, 60)
        final_price = round(prod['mrp'] * (1-disc/100), 0)
        revenue     = round(final_price * qty, 0)
        profit      = round((final_price - prod['cost_price']) * qty, 0)

        order_items.append({
            'item_id':       f'ITEM{item_id:08d}',
            'order_id':      order['order_id'],
            'product_id':    prod['product_id'],
            'category':      prod['category'],
            'subcategory':   prod['subcategory'],
            'brand':         prod['brand'],
            'quantity':      qty,
            'mrp':           prod['mrp'],
            'discount_pct':  disc,
            'final_price':   final_price,
            'revenue':       revenue,
            'cost':          round(prod['cost_price']*qty, 0),
            'profit':        profit,
            'profit_margin': round(profit/revenue*100, 2) if revenue > 0 else 0,
            'order_date':    order['order_date'],
            'order_year':    order['order_year'],
            'state':         order['state'],
            'return_flag':   1 if order['order_status']=='Returned' else 0,
        })
        item_id += 1
order_items_df = pd.DataFrame(order_items)

# ── TABLE 5: RETURNS ───────────────────────────────────────
returned_orders = orders_df[orders_df['order_status']=='Returned']
returns = []
for _, order in returned_orders.iterrows():
    items = order_items_df[order_items_df['order_id']==order['order_id']]
    ret_dt = datetime.strptime(order['order_date'],'%Y-%m-%d') + timedelta(days=random.randint(3,30))
    for _, item in items.iterrows():
        returns.append({
            'return_id':      f'RET{len(returns)+1:06d}',
            'order_id':       order['order_id'],
            'product_id':     item['product_id'],
            'customer_id':    order['customer_id'],
            'return_date':    ret_dt.strftime('%Y-%m-%d'),
            'return_reason':  random.choice(RETURN_REASONS),
            'return_amount':  item['revenue'],
            'refund_status':  random.choices(['Refunded','Pending','Rejected'],
                                             weights=[80,15,5])[0],
            'refund_days':    random.randint(3,14),
            'category':       item['category'],
        })
returns_df = pd.DataFrame(returns)

# ── TABLE 6: MARKETING CAMPAIGNS ──────────────────────────
campaigns = []
campaign_names = [
    'Diwali Mega Sale','Republic Day Sale','Independence Day Sale',
    'End of Season Sale','New Year Bonanza','Holi Special',
    'Summer Sale','Monsoon Madness','Back to School',
    'Valentine Day Sale','Eid Special','Christmas Sale',
    'Flash Sale Friday','Big Billion Day','Prime Day',
    'Women Day Sale','Tech Fest','Fashion Week Sale',
    'Grocery Month','Fitness January'
]
for i, name in enumerate(campaign_names, 1):
    start = rand_date('2020-01-01','2024-10-01')
    end   = start + timedelta(days=random.randint(3,15))
    budget= random.choice([500000,1000000,2000000,5000000,10000000])
    campaigns.append({
        'campaign_id':    f'CAMP{i:03d}',
        'campaign_name':  name,
        'start_date':     start.strftime('%Y-%m-%d'),
        'end_date':       end.strftime('%Y-%m-%d'),
        'duration_days':  (end-start).days,
        'channel':        random.choices(
            ['Email','Social Media','Google Ads','SMS','Push Notification','Influencer'],
            weights=[20,25,20,15,15,5])[0],
        'target_segment': random.choices(
            ['All Customers','Premium','New Users','Lapsed','Category Specific'],
            weights=[30,20,25,15,10])[0],
        'budget':         budget,
        'revenue_generated': round(budget * random.uniform(2.5,8.0), 0),
        'orders_generated':  random.randint(500,15000),
        'new_customers':     random.randint(100,3000),
        'discount_offered':  random.choice([10,15,20,25,30,40,50]),
        'category_focus':    random.choice(CATEGORIES+['All']),
        'roas':              round(random.uniform(2.5,8.0),2),
    })
campaigns_df = pd.DataFrame(campaigns)

# ── SAVE ──────────────────────────────────────────────────
dfs = {
    'customers':   customers_df,
    'products':    products_df,
    'orders':      orders_df,
    'order_items': order_items_df,
    'returns':     returns_df,
    'campaigns':   campaigns_df,
}
for name, df in dfs.items():
    df.to_csv(f'{BASE}/{name}.csv', index=False)
    print(f"{name:15s}: {len(df):7,} rows x {len(df.columns)} cols")

print(f"\nTotal Revenue : Rs {order_items_df['revenue'].sum()/10000000:.1f} Crore")
print(f"Total Orders  : {len(orders_df):,}")
print(f"Total Returns : {len(returns_df):,}")
print(f"Avg Margin    : {order_items_df['profit_margin'].mean():.1f}%")
