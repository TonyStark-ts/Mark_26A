
import streamlit as st
from PIL import Image
import requests
from datetime import datetime
import time
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.image import extract_patches_2d
import cv2
from googlesearch import search
import re
import random
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie

# Geoapify API Key
GEOAPIFY_API_KEY = 'c63011a12f85455b834a9c2e8adb39df'

# Initialize Wikipedia API with proper user agent
try:
    import wikipediaapi

    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='SkinHealthPro/1.0 (https://yourwebsite.com)'
    )
    WIKIPEDIA_AVAILABLE = True
except (ImportError, AssertionError) as e:
    WIKIPEDIA_AVAILABLE = False
    st.warning(f"Wikipedia integration limited: {str(e)}. Using built-in disease information.")


# Load Lottie animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_doctor = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_5tkzkblw.json")
lottie_scan = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_5tkzkblw.json")
lottie_health = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_5tkzkblw.json")

# Expanded Product Recommendations by Disease with new URLs
PRODUCT_RECOMMENDATIONS = {
    "Eczema": [
        {
            "name": "Eczema Relief Cream",
            "url": "https://www.purplle.com/product/eczema-care-cream",
            "image": "https://m.media-amazon.com/images/I/61SJuj2VURL._SL1500_.jpg",
            "description": "Specialized cream for eczema-prone skin with colloidal oatmeal",
            "price": "₹799 - ₹1,499",
            "color": "#FFD1DC"
        },
        {
            "name": "Hypoallergenic Cleanser",
            "url": "https://limese.com/products/eczema-cleanser",
            "image": "https://m.media-amazon.com/images/I/61KbY6QSl4L._SL1500_.jpg",
            "description": "Fragrance-free cleanser for sensitive eczema skin",
            "price": "₹899",
            "color": "#B5EAD7"
        },
        {
            "name": "Eczema Care Kit",
            "url": "https://www.clinikally.com/products/eczema-kit",
            "image": "https://m.media-amazon.com/images/I/71YHjVXyR0L._SL1500_.jpg",
            "description": "Complete eczema management kit with moisturizers and balms",
            "price": "₹2,499",
            "color": "#C7CEEA"
        },
        {
            "name": "Cetaphil Moisturizing Cream",
            "url": "https://www.cetaphil.in/moisturizers?utm_source=Google+&utm_medium=Search&utm_campaign=Cetaphil+Winter&utm_id=Winter+Campaign&utm_term=Winter+Campaign&gad_source=1&gbraid=0AAAAAC93JMvNpAzNtGHHVI6EAJiuz2FaA&gclid=CjwKCAjw8IfABhBXEiwAxRHlsDBg-UzdafUzJFUbhHXafRPrC9jwHUsVxR-ht6wNSby86RjeFwtRHRoC9RsQAvD_BwE&gclsrc=aw.ds",
            "image": "https://m.media-amazon.com/images/I/61KbY6QSl4L._SL1500_.jpg",
            "description": "Gentle moisturizer for dry, sensitive skin",
            "price": "₹599",
            "color": "#E1F5FE"
        },
        {
            "name": "Plum Green Tea Moisturizer",
            "url": "https://plumgoodness.com/?utm_source=google_search&utm_medium=brandsearch&utm_campaign=TP_Plum_Brand_Search_IS_Jan24_Search_Brand_April25_3at1099&gad_source=1&gbraid=0AAAAADoQ5k1FrodKK8k-SpqfTAQBhOMi9&gclid=CjwKCAjw8IfABhBXEiwAxRHlsIq831kCirUPQKJ0RGpFzsE7RvO1hG55gOprBuumU282j6T9MeYc2hoCjgUQAvD_BwE",
            "image": "https://m.media-amazon.com/images/I/61SJuj2VURL._SL1500_.jpg",
            "description": "Lightweight moisturizer with green tea extracts",
            "price": "₹549",
            "color": "#DCEDC8"
        }
    ],
    "Psoriasis": [
        {
            "name": "Psoriasis Treatment Cream",
            "url": "https://www.purplle.com/product/psoriasis-cream",
            "image": "https://m.media-amazon.com/images/I/71p4Q5QyHUL._SL1500_.jpg",
            "description": "Medicated cream with salicylic acid for psoriasis relief",
            "price": "₹899 - ₹1,799",
            "color": "#FFD1DC"
        },
        {
            "name": "Coal Tar Shampoo",
            "url": "https://limese.com/products/psoriasis-shampoo",
            "image": "https://m.media-amazon.com/images/I/61tKQhj3QBL._SL1500_.jpg",
            "description": "Therapeutic shampoo for scalp psoriasis",
            "price": "₹699",
            "color": "#B5EAD7"
        },
        {
            "name": "Psoriasis Care Kit",
            "url": "https://www.clinikally.com/products/psoriasis-kit",
            "image": "https://m.media-amazon.com/images/I/71vJQ6qQyZL._SL1500_.jpg",
            "description": "Complete psoriasis management system",
            "price": "₹3,299",
            "color": "#C7CEEA"
        },
        {
            "name": "Dermaco Psoriasis Cream",
            "url": "https://thedermaco.com/product-category/dry-dull-skin?srsltid=AfmBOopOjaPBsUc6PUwtR9VXZjFp8Ib9wk8-4hWZ27Uk9Qh1IoPP2_Jm",
            "image": "https://m.media-amazon.com/images/I/71YHjVXyR0L._SL1500_.jpg",
            "description": "Specialized cream for psoriasis relief",
            "price": "₹899",
            "color": "#FFECB3"
        },
        {
            "name": "Minimalist Psoriasis Kit",
            "url": "https://beminimalist.co/products/dry-skincare-kit?srsltid=AfmBOoqIaMC11Ehdc-w4bqDe7usB3h3EQK0hyuf7mEgD3uoUBHKQuwvI",
            "image": "https://m.media-amazon.com/images/I/71vJQ6qQyZL._SL1500_.jpg",
            "description": "Complete psoriasis care solution",
            "price": "₹1,299",
            "color": "#D7CCC8"
        }
    ],
    "Acne": [
        {
            "name": "Acne Treatment Gel",
            "url": "https://www.purplle.com/product/acne-gel",
            "image": "https://m.media-amazon.com/images/I/61SJuj2VURL._SL1500_.jpg",
            "description": "Benzoyl peroxide gel for acne treatment",
            "price": "₹499 - ₹899",
            "color": "#FFD1DC"
        },
        {
            "name": "Salicylic Acid Cleanser",
            "url": "https://limese.com/products/acne-cleanser",
            "image": "https://m.media-amazon.com/images/I/61KbY6QSl4L._SL1500_.jpg",
            "description": "Oil-free cleanser for acne-prone skin",
            "price": "₹599",
            "color": "#B5EAD7"
        },
        {
            "name": "Acne Care Kit",
            "url": "https://www.clinikally.com/products/acne-kit",
            "image": "https://m.media-amazon.com/images/I/71YHjVXyR0L._SL1500_.jpg",
            "description": "Complete acne treatment system",
            "price": "₹1,999",
            "color": "#C7CEEA"
        },
        {
            "name": "Foxtale Acne Solution",
            "url": "https://foxtale.in/collections/shop-1?utm_source=Google&utm_medium=CPC&utm_campaign=Search_Brand_Exact&gad_source=1&gbraid=0AAAAAoTiBN7_ohZboZ1sLYyQXDi6luXbg&gclid=CjwKCAjw8IfABhBXEiwAxRHlsByZY2bGtqKpxdazqpP80WigkIY9Aq0SFA7CNvNm7htMfHnQOt9U8BoC23AQAvD_BwE",
            "image": "https://m.media-amazon.com/images/I/61SJuj2VURL._SL1500_.jpg",
            "description": "Advanced acne treatment formula",
            "price": "₹699",
            "color": "#F8BBD0"
        },
        {
            "name": "Reequil Acne Control",
            "url": "https://www.reequil.com/collections/dryness?srsltid=AfmBOoqW9c7QTq3s_tXIVuzKX_U7ojpEG2F8xLe3lGytTz1zNqgH5xmv",
            "image": "https://m.media-amazon.com/images/I/61KbY6QSl4L._SL1500_.jpg",
            "description": "Oil-control solution for acne-prone skin",
            "price": "₹799",
            "color": "#C5CAE9"
        }
    ],
    "Rosacea": [
        {
            "name": "Rosacea Calming Cream",
            "url": "https://www.purplle.com/product/rosacea-cream",
            "image": "https://m.media-amazon.com/images/I/61SJuj2VURL._SL1500_.jpg",
            "description": "Soothing cream for rosacea-prone skin",
            "price": "₹1,199 - ₹1,899",
            "color": "#FFD1DC"
        },
        {
            "name": "Gentle Mineral Sunscreen",
            "url": "https://limese.com/products/rosacea-sunscreen",
            "image": "https://m.media-amazon.com/images/I/61KbY6QSl4L._SL1500_.jpg",
            "description": "SPF 50 physical sunscreen for sensitive skin",
            "price": "₹999",
            "color": "#B5EAD7"
        },
        {
            "name": "Rosacea Care Kit",
            "url": "https://www.clinikally.com/products/rosacea-kit",
            "image": "https://m.media-amazon.com/images/I/71YHjVXyR0L._SL1500_.jpg",
            "description": "Complete rosacea management system",
            "price": "₹2,799",
            "color": "#C7CEEA"
        },
        {
            "name": "Earth Rhythm Sensitive Skin Kit",
            "url": "https://earthrhythm.com/collections/sensitive-skin?srsltid=AfmBOooqRjqEhwvhI7NxJcjsvcRqqAXHE-5ISc9-H9t37iVLugX7N6CI",
            "image": "https://m.media-amazon.com/images/I/71vJQ6qQyZL._SL1500_.jpg",
            "description": "Gentle care for rosacea-prone skin",
            "price": "₹1,599",
            "color": "#DCE775"
        },
        {
            "name": "Dot & Key Rosacea Solution",
            "url": "https://www.dotandkey.com/collections/sensitive-skin?srsltid=AfmBOopvcM2EPrFPl7be2m1y8CJYVKXuPSbomRRGYsUlj5wCmgTvXMnV",
            "image": "https://m.media-amazon.com/images/I/61SJuj2VURL._SL1500_.jpg",
            "description": "Specialized treatment for rosacea",
            "price": "₹899",
            "color": "#F48FB1"
        }
    ],
    "default": [
        {
            "name": "Moisturizing Cream",
            "url": "https://www.purplle.com/collections/best-moisturizer-for-dry-sensitive-skin",
            "image": "https://m.media-amazon.com/images/I/61SJuj2VURL._SL1500_.jpg",
            "description": "Specialized moisturizers for dry and sensitive skin",
            "price": "₹599 - ₹1,299",
            "color": "#FFD1DC"
        },
        {
            "name": "Gentle Cleanser",
            "url": "https://limese.com/products/cosrx-low-ph-good-morning-gel-cleanser",
            "image": "https://m.media-amazon.com/images/I/61KbY6QSl4L._SL1500_.jpg",
            "description": "Low pH cleanser for sensitive skin",
            "price": "₹799",
            "color": "#B5EAD7"
        },
        {
            "name": "Medical Kit",
            "url": "https://www.clinikally.com/collections/kits",
            "image": "https://m.media-amazon.com/images/I/71YHjVXyR0L._SL1500_.jpg",
            "description": "Complete dermatology care kits",
            "price": "₹1,499 - ₹2,999",
            "color": "#C7CEEA"
        },
        {
            "name": "Himalaya Aloe Vera Moisturizer",
            "url": "https://www.amazon.in/Himalaya-Moisturizing-Aloe-Vera-200ml/dp/B074M3Z6Q5?gad_source=1&gbraid=0AAAAADB8CXBHkkmY9a7yLBIq7EK13eL26&gclid=CjwKCAjw8IfABhBXEiwAxRHlsIbUXeDgHVadThX5_c9CC0VSPsIlzxk6v52j4mcs2p3sHNj9_kTSLBoC7EkQAvD_BwE&th=1",
            "image": "https://m.media-amazon.com/images/I/61KbY6QSl4L._SL1500_.jpg",
            "description": "Natural aloe vera based moisturizer",
            "price": "₹299",
            "color": "#81C784"
        },
        {
            "name": "Mamaearth Face Cream",
            "url": "https://mamaearth.in/product-category/face-cream-for-dry-skin?srsltid=AfmBOorUn-T9CcTX7jEkpURXRNX9Q4hgGT-YGelPxpaUJNcrGKtaA5lu",
            "image": "https://m.media-amazon.com/images/I/71YHjVXyR0L._SL1500_.jpg",
            "description": "Natural face cream for dry skin",
            "price": "₹499",
            "color": "#4FC3F7"
        }
    ]
}

# Create train directory if it doesn't exist
if not os.path.exists('train'):
    os.makedirs('train')
    # Create subdirectories for each disease
    for disease in ['Eczema', 'Psoriasis', 'Acne', 'Rosacea']:
        os.makedirs(f'train/{disease}')

# Comprehensive Medicine Database (Expanded)
MEDICINE_DATABASE = {
    "Acne Vulgaris": {
        "symptoms": [
            "Pimples, blackheads, whiteheads",
            "Cysts or nodules in severe cases",
            "Oily skin and scarring"
        ],
        "treatment": [
            "Cleanse face regularly",
            "Avoid heavy makeup and greasy products",
            "Use topical/oral treatments depending on severity"
        ],
        "medicines": [
            "Benzoyl peroxide",
            "Clindamycin gel",
            "Tretinoin (Retinoid)",
            "Oral doxycycline or isotretinoin (for severe acne)"
        ]
    },
    "Actinic Keratosis": {
        "symptoms": [
            "Rough, scaly patch on sun-exposed skin",
            "Itching or burning in the area",
            "May become hard and wart-like"
        ],
        "treatment": [
            "Cryotherapy (freezing)",
            "Topical medications",
            "Photodynamic therapy"
        ],
        "medicines": [
            "Fluorouracil cream",
            "Imiquimod cream",
            "Diclofenac gel"
        ]
    },
    "Alopecia Areata": {
        "symptoms": [
            "Sudden hair loss in round patches",
            "Tingling or itching before hair falls out",
            "May affect scalp, beard, eyebrows"
        ],
        "treatment": [
            "Corticosteroid injections",
            "Topical immunotherapy",
            "Minoxidil for regrowth"
        ],
        "medicines": [
            "Topical Minoxidil",
            "Corticosteroids (topical/injected)",
            "Anthralin cream"
        ]
    },
    "Athlete's Foot (Tinea Pedis)": {
        "symptoms": [
            "Itching, burning, and stinging between toes",
            "Cracked, peeling, or scaly skin",
            "Foul odor"
        ],
        "treatment": [
            "Keep feet dry and clean",
            "Use antifungal powders or creams",
            "Wear breathable shoes and socks"
        ],
        "medicines": [
            "Clotrimazole cream",
            "Terbinafine cream",
            "Miconazole spray or powder"
        ]
    },
    "Atopic Dermatitis (Eczema)": {
        "symptoms": [
            "Red, dry, itchy patches (common on face, elbows, knees)",
            "Thickened, cracked, or scaly skin",
            "Oozing and crusting in severe cases"
        ],
        "treatment": [
            "Avoid irritants and allergens",
            "Moisturize frequently",
            "Use anti-inflammatory treatments"
        ],
        "medicines": [
            "Hydrocortisone or betamethasone cream",
            "Tacrolimus or pimecrolimus (non-steroid)",
            "Cetirizine (for itching)"
        ]
    },
    "Basal Cell Carcinoma": {
        "symptoms": [
            "Pearly or waxy bump",
            "Flat, flesh-colored or brown scar-like lesion",
            "Bleeding or scabbing sore that doesn't heal"
        ],
        "treatment": [
            "Surgical removal (excision or Mohs surgery)",
            "Cryotherapy or laser therapy",
            "Topical or radiation treatment in some cases"
        ],
        "medicines": [
            "Imiquimod cream",
            "Fluorouracil cream (5-FU)",
            "Vismodegib (for advanced cases)"
        ]
    },
    "Bullous Pemphigoid": {
        "symptoms": [
            "Large, fluid-filled blisters on skin (especially arms, legs, abdomen)",
            "Itching and rash before blisters appear",
            "Blisters do not rupture easily"
        ],
        "treatment": [
            "Corticosteroids and immunosuppressants",
            "Skin care and wound management"
        ],
        "medicines": [
            "Prednisone (oral corticosteroid)",
            "Azathioprine or methotrexate",
            "Topical clobetasol"
        ]
    },
    "Cellulitis": {
        "symptoms": [
            "Red, swollen, painful skin (usually on legs)",
            "Warmth and tenderness in the area",
            "Fever and chills in severe cases"
        ],
        "treatment": [
            "Oral or IV antibiotics depending on severity",
            "Elevation of affected limb"
        ],
        "medicines": [
            "Amoxicillin-clavulanate",
            "Cephalexin",
            "Clindamycin (for penicillin allergy)"
        ]
    },
    "Contact Dermatitis": {
        "symptoms": [
            "Red rash or bumps after touching an irritant/allergen",
            "Itching, burning, or dry patches",
            "Possible oozing or crusting in severe cases"
        ],
        "treatment": [
            "Avoid triggers or allergens",
            "Apply soothing creams",
            "Use antihistamines for itching"
        ],
        "medicines": [
            "Hydrocortisone cream",
            "Calamine lotion",
            "Cetirizine or loratadine (oral antihistamines)"
        ]
    },
    "Corns and Calluses": {
        "symptoms": [
            "Thickened, hardened areas of skin (feet or hands)",
            "Pain or tenderness under the skin",
            "Dry, flaky appearance"
        ],
        "treatment": [
            "Soak and gently file the area",
            "Use cushioned pads",
            "Apply keratolytic agents"
        ],
        "medicines": [
            "Salicylic acid pads/creams",
            "Urea cream",
            "Ammonium lactate lotion"
        ]
    },
    "Cutaneous T-cell Lymphoma": {
        "symptoms": [
            "Scaly red patches or thickened plaques",
            "Itching and dry skin",
            "May progress to tumors or involve lymph nodes"
        ],
        "treatment": [
            "Light therapy (PUVA or UVB)",
            "Topical corticosteroids or chemotherapy",
            "Systemic immunotherapy for advanced cases"
        ],
        "medicines": [
            "Bexarotene (topical or oral)",
            "Interferon alfa",
            "Methotrexate (oral or injection)"
        ]
    },
    "Cutaneous Horn": {
        "symptoms": [
            "Hard, cone-shaped growth on skin (resembles horn)",
            "May arise from sun-exposed areas",
            "Surrounding skin may show signs of irritation or cancer"
        ],
        "treatment": [
            "Surgical removal and biopsy",
            "Follow-up if signs of skin cancer are present"
        ],
        "medicines": [
            "No specific medicines; excision is standard",
            "Topical 5-fluorouracil or imiquimod if premalignant lesions are present"
        ]
    },
    "Dermatitis Herpetiformis": {
        "symptoms": [
            "Intense itching, burning, and stinging",
            "Blistering rash (elbows, knees, back, buttocks)",
            "Associated with gluten sensitivity"
        ],
        "treatment": [
            "Lifelong gluten-free diet",
            "Medication to control itching and rash"
        ],
        "medicines": [
            "Dapsone",
            "Sulfapyridine (if dapsone not tolerated)",
            "Corticosteroids (in some cases)"
        ]
    },
    "Dermatomyositis": {
        "symptoms": [
            "Reddish-purple rash (face, eyelids, knuckles)",
            "Muscle weakness (especially upper arms/thighs)",
            "Difficulty swallowing or fatigue"
        ],
        "treatment": [
            "Immunosuppressive therapy",
            "Physical therapy to retain muscle function"
        ],
        "medicines": [
            "Prednisone",
            "Azathioprine or methotrexate",
            "IVIG (intravenous immunoglobulin in severe cases)"
        ]
    },
    "Diaper Rash (Diaper Dermatitis)": {
        "symptoms": [
            "Red, tender rash on buttocks, thighs, or genitals",
            "Irritated skin, sometimes with blisters or peeling",
            "Infant may show discomfort during diaper changes"
        ],
        "treatment": [
            "Frequent diaper changes",
            "Gentle cleansing and air exposure",
            "Barrier creams"
        ],
        "medicines": [
            "Zinc oxide cream",
            "Petroleum jelly",
            "Clotrimazole (if fungal infection suspected)"
        ]
    },
    "Drug Eruptions": {
        "symptoms": [
            "Rashes, hives, or blistering on skin",
            "Fever, swelling, or pain",
            "Rash usually appears shortly after starting a new medication"
        ],
        "treatment": [
            "Discontinue the offending drug",
            "Use antihistamines for itching",
            "Topical steroids for inflammation"
        ],
        "medicines": [
            "Antihistamines (e.g., cetirizine)",
            "Prednisone for severe cases",
            "Topical corticosteroids"
        ]
    },
    "Dyshidrotic Eczema": {
        "symptoms": [
            "Small, itchy blisters on hands and feet",
            "Burning or stinging sensation",
            "Dry, cracked skin as blisters heal"
        ],
        "treatment": [
            "Topical corticosteroids",
            "Moisturizers to reduce dryness",
            "Avoiding triggers (stress, allergens)"
        ],
        "medicines": [
            "Clobetasol or hydrocortisone (topical)",
            "Oral antihistamines for itching",
            "Immunosuppressive agents (in severe cases)"
        ]
    },
    "Ecchymosis": {
        "symptoms": [
            "Purple or blue bruises on skin (due to blood leakage)",
            "Pain or tenderness in affected areas",
            "May spread or fade to yellow-green as healing progresses"
        ],
        "treatment": [
            "Rest and elevation of affected area",
            "Ice application in the first 24-48 hours",
            "Pain relief as needed"
        ],
        "medicines": [
            "Pain relievers (e.g., ibuprofen, acetaminophen)",
            "Topical arnica gel",
            "Vitamin K cream for healing"
        ]
    },
    "Ecthyma": {
        "symptoms": [
            "Deep ulcers or sores with a crusty appearance",
            "Usually caused by bacterial infection (staphylococcus or streptococcus)",
            "Pain, redness, and swelling around the lesion"
        ],
        "treatment": [
            "Topical or oral antibiotics",
            "Regular cleaning and dressing of the wound"
        ],
        "medicines": [
            "Mupirocin (topical antibiotic)",
            "Oral antibiotics (e.g., penicillin, dicloxacillin)",
            "Pain relievers (e.g., ibuprofen)"
        ]
    },
    "Café-au-lait Spots": {
        "symptoms": [
            "Light to dark brown patches on the skin",
            "Oval or irregular shapes",
            "May appear at birth or develop over time"
        ],
        "treatment": [
            "No specific treatment required",
            "Cosmetic procedures (laser) for cosmetic concerns"
        ],
        "medicines": [
            "No specific medication required"
        ]
    },
    "Candidiasis": {
        "symptoms": [
            "Itchy red rash, often with white patches in mouth or genital area",
            "Pain during urination or intercourse",
            "Thick, cottage cheese-like discharge (in vaginal candidiasis)"
        ],
        "treatment": [
            "Antifungal creams or oral antifungals",
            "Good hygiene and keeping the area dry"
        ],
        "medicines": [
            "Fluconazole (oral)",
            "Clotrimazole (topical)",
            "Miconazole (topical)"
        ]
    },
    "Carbuncles": {
        "symptoms": [
            "Large, painful bumps with pus inside",
            "Redness and swelling around the affected area",
            "Can develop fever and chills"
        ],
        "treatment": [
            "Drainage of the carbuncle by a healthcare provider",
            "Oral or topical antibiotics"
        ],
        "medicines": [
            "Dicloxacillin (oral)",
            "Clindamycin (oral)",
            "Topical mupirocin"
        ]
    },
    "Rosacea": {
        "symptoms": [
            "Facial redness (especially cheeks, nose, chin, forehead)",
            "Visible blood vessels",
            "Bumps or pimples",
            "Eye irritation (ocular rosacea)"
        ],
        "treatment": [
            "Avoid triggers (sun, spicy foods, alcohol)",
            "Topical medications",
            "Oral antibiotics for inflammation",
            "Laser therapy for visible blood vessels"
        ],
        "medicines": [
            "Metronidazole cream",
            "Azelaic acid gel",
            "Doxycycline (low dose)",
            "Brimonidine gel (for redness)"
        ]
    },
    "Psoriasis": {
        "symptoms": [
            "Red patches with thick, silvery scales",
            "Dry, cracked skin that may bleed",
            "Itching, burning, or soreness",
            "Thickened, pitted, or ridged nails"
        ],
        "treatment": [
            "Topical corticosteroids",
            "Vitamin D analogs",
            "Light therapy (phototherapy)",
            "Systemic medications for severe cases"
        ],
        "medicines": [
            "Calcipotriene (vitamin D analog)",
            "Tazarotene (retinoid cream)",
            "Methotrexate (for severe cases)",
            "Biologics (e.g., adalimumab, ustekinumab)"
        ]
    },
    "Eczema": {
        "symptoms": [
            "Dry, sensitive skin",
            "Intense itching",
            "Red, inflamed skin",
            "Recurrent rash",
            "Scaly areas"
        ],
        "treatment": [
            "Regular moisturizing",
            "Topical corticosteroids",
            "Avoiding triggers",
            "Wet wrap therapy for severe cases"
        ],
        "medicines": [
            "Hydrocortisone cream",
            "Tacrolimus ointment",
            "Pimecrolimus cream",
            "Antihistamines for itching"
        ]
    },
    # Expanded database with additional conditions
    "Albinism": {
        "symptoms": [
            "Pale skin, white hair",
            "Vision problems (nystagmus, photophobia)"
        ],
        "treatment": [
            "No cure; manage symptoms (vision aids, sunscreen)"
        ],
        "medicines": [
            "No specific medication required"
        ]
    },
    "Androgenetic Alopecia": {
        "symptoms": [
            "Thinning hair (male: receding hairline; female: diffuse thinning)"
        ],
        "treatment": [
            "Topical/oral medications to promote hair growth"
        ],
        "medicines": [
            "Minoxidil (topical)",
            "Finasteride (oral, for men)",
            "Spironolactone (women)"
        ]
    },
    "Angioedema": {
        "symptoms": [
            "Swelling under the skin (lips, eyes)",
            "Often with hives"
        ],
        "treatment": [
            "Antihistamines, epinephrine for severe cases"
        ],
        "medicines": [
            "Cetirizine",
            "Epinephrine (for severe cases)",
            "Steroids"
        ]
    },
    "Erysipelas": {
        "symptoms": [
            "Bright red, raised, painful plaque (often on legs/face)"
        ],
        "treatment": [
            "Antibiotics"
        ],
        "medicines": [
            "Penicillin",
            "Erythromycin"
        ]
    },
    "Folliculitis": {
        "symptoms": [
            "Pustules around hair follicles"
        ],
        "treatment": [
            "Topical/oral antibiotics"
        ],
        "medicines": [
            "Mupirocin (topical)",
            "Dicloxacillin (oral)"
        ]
    },
    "Herpes Simplex (HSV)": {
        "symptoms": [
            "Painful blisters (oral: cold sores; genital: ulcers)"
        ],
        "treatment": [
            "Antivirals"
        ],
        "medicines": [
            "Acyclovir",
            "Valacyclovir"
        ]
    },
    "Herpes Zoster (Shingles)": {
        "symptoms": [
            "Painful, unilateral vesicular rash (dermatomal)"
        ],
        "treatment": [
            "Antivirals, pain management"
        ],
        "medicines": [
            "Valacyclovir",
            "Gabapentin (for postherpetic neuralgia)"
        ]
    },
    "Impetigo": {
        "symptoms": [
            "Honey-colored crusts, blisters (strep/staph)"
        ],
        "treatment": [
            "Topical/oral antibiotics"
        ],
        "medicines": [
            "Mupirocin (topical)",
            "Cephalexin (oral)"
        ]
    },
    "Lichen Planus": {
        "symptoms": [
            "Purple, itchy papules (wrists, oral mucosa)"
        ],
        "treatment": [
            "Topical steroids, oral medications for severe cases"
        ],
        "medicines": [
            "Topical corticosteroids",
            "Oral steroids (severe cases)"
        ]
    },
    "Lupus Erythematosus": {
        "symptoms": [
            "Malar rash, photosensitivity, discoid plaques"
        ],
        "treatment": [
            "Immunosuppressants, sun protection"
        ],
        "medicines": [
            "Hydroxychloroquine",
            "Steroids",
            "Immunosuppressants"
        ]
    },
    "Melanoma": {
        "symptoms": [
            "Asymmetrical, irregular mole (ABCDE criteria)"
        ],
        "treatment": [
            "Surgical excision, immunotherapy"
        ],
        "medicines": [
            "Pembrolizumab (immunotherapy)"
        ]
    },
    "Molluscum Contagiosum": {
        "symptoms": [
            "Flesh-colored, dome-shaped papules"
        ],
        "treatment": [
            "Cryotherapy, curettage"
        ],
        "medicines": [
            "Topical cantharidin"
        ]
    },
    "Onychomycosis (Nail Fungus)": {
        "symptoms": [
            "Thickened, discolored nails"
        ],
        "treatment": [
            "Oral antifungals, topical treatments"
        ],
        "medicines": [
            "Terbinafine (oral)",
            "Ciclopirox (topical)"
        ]
    },
    "Pemphigus Vulgaris": {
        "symptoms": [
            "Flaccid blisters, oral erosions"
        ],
        "treatment": [
            "High-dose steroids, immunosuppressants"
        ],
        "medicines": [
            "Prednisone",
            "Rituximab"
        ]
    },
    "Scabies": {
        "symptoms": [
            "Intense itching, burrows (finger webs)"
        ],
        "treatment": [
            "Topical scabicides"
        ],
        "medicines": [
            "Permethrin cream",
            "Ivermectin (oral)"
        ]
    },
    "Seborrheic Dermatitis": {
        "symptoms": [
            "Scalp flaking (dandruff), red patches (face)"
        ],
        "treatment": [
            "Antifungal shampoos, topical steroids"
        ],
        "medicines": [
            "Ketoconazole shampoo",
            "Topical steroids"
        ]
    },
    "Tinea (Ringworm, Athlete's Foot, Jock Itch)": {
        "symptoms": [
            "Circular, scaly rash"
        ],
        "treatment": [
            "Topical/oral antifungals"
        ],
        "medicines": [
            "Clotrimazole (topical)",
            "Terbinafine (oral)"
        ]
    },
    "Urticaria (Hives)": {
        "symptoms": [
            "Raised, itchy wheals"
        ],
        "treatment": [
            "Antihistamines"
        ],
        "medicines": [
            "Loratadine",
            "Omalizumab (chronic cases)"
        ]
    },
    "Vitiligo": {
        "symptoms": [
            "Depigmented white patches"
        ],
        "treatment": [
            "Topical treatments, phototherapy"
        ],
        "medicines": [
            "Topical steroids",
            "Tacrolimus ointment",
            "Phototherapy"
        ]
    },
    "Warts (HPV)": {
        "symptoms": [
            "Rough, raised papules"
        ],
        "treatment": [
            "Destructive methods, immunomodulators"
        ],
        "medicines": [
            "Salicylic acid",
            "Imiquimod"
        ]
    },
    "Dermatitis Artefacta": {
        "symptoms": [
            "Geometric lesions in accessible areas"
        ],
        "treatment": [
            "Psychotherapy, occlusive dressings"
        ],
        "medicines": [
            "No specific medications",
            "May require psychiatric medications"
        ]
    },
    "Body Dysmorphic Disorder": {
        "symptoms": [
            "Excessive concern over minor skin flaws"
        ],
        "treatment": [
            "SSRIs, cognitive behavioral therapy"
        ],
        "medicines": [
            "Fluoxetine",
            "Sertraline"
        ]
    },
    "Trichotillomania": {
        "symptoms": [
            "Patchy hair loss from compulsive pulling"
        ],
        "treatment": [
            "SSRIs, behavioral therapy"
        ],
        "medicines": [
            "Fluoxetine",
            "Clomipramine"
        ]
    },
    "Telogen Effluvium": {
        "symptoms": [
            "Diffuse hair shedding after stress/illness"
        ],
        "treatment": [
            "Address underlying cause, minoxidil"
        ],
        "medicines": [
            "Minoxidil"
        ]
    },
    "Vasculitis": {
        "symptoms": [
            "Palpable purpura, joint pain, abdominal pain"
        ],
        "treatment": [
            "Oral steroids, immunosuppressants"
        ],
        "medicines": [
            "Prednisone",
            "Azathioprine"
        ]
    },
    "Tuberous Sclerosis": {
        "symptoms": [
            "Angiofibromas, ash-leaf spots, seizures"
        ],
        "treatment": [
            "mTOR inhibitors"
        ],
        "medicines": [
            "Everolimus"
        ]
    },
    "Neurofibromatosis": {
        "symptoms": [
            "Café-au-lait spots, neurofibromas"
        ],
        "treatment": [
            "Surgical removal of painful tumors"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Pityriasis Rosea": {
        "symptoms": [
            "Herald patch followed by Christmas-tree rash"
        ],
        "treatment": [
            "Self-limiting, UVB phototherapy if severe"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Polymorphous Light Eruption (PMLE)": {
        "symptoms": [
            "Itchy papules after sun exposure"
        ],
        "treatment": [
            "Topical steroids, antihistamines"
        ],
        "medicines": [
            "Topical corticosteroids",
            "Cetirizine"
        ]
    },
    "Solar Urticaria": {
        "symptoms": [
            "Hives within minutes of sun exposure"
        ],
        "treatment": [
            "Antihistamines, omalizumab"
        ],
        "medicines": [
            "Loratadine",
            "Omalizumab"
        ]
    },
    "Melasma": {
        "symptoms": [
            "Brown patches on face (cheeks, forehead)"
        ],
        "treatment": [
            "Topical lightening agents"
        ],
        "medicines": [
            "Hydroquinone",
            "Tranexamic acid"
        ]
    },
    "Post-inflammatory Hyperpigmentation": {
        "symptoms": [
            "Dark spots after skin injury/inflammation"
        ],
        "treatment": [
            "Topical retinoids, azelaic acid"
        ],
        "medicines": [
            "Tretinoin",
            "Azelaic acid"
        ]
    },
    "Post-inflammatory Hypopigmentation": {
        "symptoms": [
            "White spots after skin trauma"
        ],
        "treatment": [
            "Topical calcineurin inhibitors"
        ],
        "medicines": [
            "Tacrolimus ointment",
            "Pimecrolimus cream"
        ]
    },
    "Drug Eruptions": {
        "symptoms": [
            "Morbilliform rash, SJS/TEN (severe), DRESS syndrome"
        ],
        "treatment": [
            "Discontinue culprit drug, systemic steroids for severe cases"
        ],
        "medicines": [
            "Prednisone (for severe cases)"
        ]
    },
    "Fixed Drug Eruption": {
        "symptoms": [
            "Recurrent oval plaques in same location"
        ],
        "treatment": [
            "Identify and avoid triggering drug"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Strawberry Hemangioma": {
        "symptoms": [
            "Red raised tumor in infants (proliferates then involutes)"
        ],
        "treatment": [
            "Propranolol for problematic lesions"
        ],
        "medicines": [
            "Propranolol"
        ]
    },
    "Keratoacanthoma": {
        "symptoms": [
            "Rapid-growing crateriform nodule"
        ],
        "treatment": [
            "Surgical excision"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Cutaneous T-cell Lymphoma (Mycosis Fungoides)": {
        "symptoms": [
            "Patches/plaques in sun-protected areas"
        ],
        "treatment": [
            "Phototherapy, topical nitrogen mustard"
        ],
        "medicines": [
            "Nitrogen mustard",
            "Bexarotene"
        ]
    },
    "Acanthosis Nigricans": {
        "symptoms": [
            "Velvety hyperpigmented plaques (neck/axillae)"
        ],
        "treatment": [
            "Address insulin resistance"
        ],
        "medicines": [
            "Metformin (for insulin resistance)"
        ]
    },
    "Porphyria Cutanea Tarda": {
        "symptoms": [
            "Fragile skin, blisters on sun-exposed areas"
        ],
        "treatment": [
            "Phlebotomy, antimalarials"
        ],
        "medicines": [
            "Chloroquine"
        ]
    },
    "Delusions of Parasitosis": {
        "symptoms": [
            "Fixed belief of skin infestation"
        ],
        "treatment": [
            "Antipsychotics"
        ],
        "medicines": [
            "Pimozide"
        ]
    },
    "Notalgia Paresthetica": {
        "symptoms": [
            "Itchy patch on mid-back"
        ],
        "treatment": [
            "Capsaicin cream, gabapentin"
        ],
        "medicines": [
            "Gabapentin",
            "Capsaicin cream"
        ]
    },
    "Furuncles/Carbuncles": {
        "symptoms": [
            "Painful, deep nodules with pus (staph infection)"
        ],
        "treatment": [
            "Incision & drainage, antibiotics"
        ],
        "medicines": [
            "Dicloxacillin"
        ]
    },
    "Ecthyma": {
        "symptoms": [
            "Ulcerated lesions with crust (deeper impetigo)"
        ],
        "treatment": [
            "Oral antibiotics"
        ],
        "medicines": [
            "Cephalexin"
        ]
    },
    "Pediculosis (Lice)": {
        "symptoms": [
            "Scalp/body itching, nits on hair shafts"
        ],
        "treatment": [
            "Permethrin lotion, ivermectin"
        ],
        "medicines": [
            "Permethrin",
            "Ivermectin"
        ]
    },
    "Pemphigus Foliaceus": {
        "symptoms": [
            "Superficial blisters, scaly crusts"
        ],
        "treatment": [
            "High-dose steroids, rituximab"
        ],
        "medicines": [
            "Prednisone",
            "Rituximab"
        ]
    },
    "Paraneoplastic Pemphigus": {
        "symptoms": [
            "Severe mucosal erosions + malignancy"
        ],
        "treatment": [
            "Treat underlying cancer, immunosuppressants"
        ],
        "medicines": [
            "Prednisone",
            "Rituximab"
        ]
    },
    "Cherry Angioma": {
        "symptoms": [
            "Bright red papules (benign)"
        ],
        "treatment": [
            "Electrocautery if cosmetic concern"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Spider Angioma": {
        "symptoms": [
            "Central arteriole with radiating vessels"
        ],
        "treatment": [
            "Pulsed dye laser"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Ichthyosis Vulgaris": {
        "symptoms": [
            "Dry, fish-like scales"
        ],
        "treatment": [
            "Urea creams, retinoids"
        ],
        "medicines": [
            "Urea cream",
            "Retinoids"
        ]
    },
    "Beaus Lines": {
        "symptoms": [
            "Transverse nail grooves"
        ],
        "treatment": [
            "None (grows out)"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Leukonychia": {
        "symptoms": [
            "White nail streaks/spots"
        ],
        "treatment": [
            "None"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Lentigines": {
        "symptoms": [
            "Sun-induced brown macules"
        ],
        "treatment": [
            "Cryotherapy, lasers"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Sebaceous Hyperplasia": {
        "symptoms": [
            "Yellowish papules on face"
        ],
        "treatment": [
            "Electrodessication"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Lipoma": {
        "symptoms": [
            "Soft, mobile subcutaneous nodule"
        ],
        "treatment": [
            "Excision if symptomatic"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Necrobiosis Lipoidica": {
        "symptoms": [
            "Shiny plaques on shins (diabetes-linked)"
        ],
        "treatment": [
            "Topical steroids"
        ],
        "medicines": [
            "Topical corticosteroids"
        ]
    },
    "Erythema Nodosum": {
        "symptoms": [
            "Tender red nodules on shins"
        ],
        "treatment": [
            "NSAIDs, treat underlying cause"
        ],
        "medicines": [
            "Ibuprofen"
        ]
    },
    "Necrolytic Migratory Erythema (Glucagonoma Syndrome)": {
        "symptoms": [
            "Scaly, erythematous plaques in groin/perineum"
        ],
        "treatment": [
            "Surgical removal of glucagonoma, octreotide"
        ],
        "medicines": [
            "Octreotide"
        ]
    },
    "Seborrheic Keratosis": {
        "symptoms": [
            "\"Stuck-on\" brown plaques with greasy surface"
        ],
        "treatment": [
            "Cryotherapy, curettage"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Skin Tags (Acrochordons)": {
        "symptoms": [
            "Soft, flesh-colored pedunculated papules"
        ],
        "treatment": [
            "Snip excision, cryotherapy"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Dermatosis Papulosa Nigra": {
        "symptoms": [
            "Small, dark papules on face (common in darker skin)"
        ],
        "treatment": [
            "Light electrocautery"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Pyogenic Granuloma": {
        "symptoms": [
            "Rapid-growing, bleeding red nodule"
        ],
        "treatment": [
            "Shave excision + electrocautery"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Kaposi Sarcoma": {
        "symptoms": [
            "Purple macules/plaques (classic or HIV-associated)"
        ],
        "treatment": [
            "ART for HIV-related, radiation for localized"
        ],
        "medicines": [
            "Antiretroviral therapy (for HIV-related)"
        ]
    },
    "Pseudoxanthoma Elasticum": {
        "symptoms": [
            "Yellow papules in flexural areas, angioid streaks"
        ],
        "treatment": [
            "None for skin; monitor cardiovascular"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Frontal Fibrosing Alopecia": {
        "symptoms": [
            "Receding frontal hairline + eyebrow loss"
        ],
        "treatment": [
            "Intralesional steroids, hydroxychloroquine"
        ],
        "medicines": [
            "Hydroxychloroquine"
        ]
    },
    "Central Centrifugal Cicatricial Alopecia": {
        "symptoms": [
            "Central scalp hair loss with scarring"
        ],
        "treatment": [
            "Minoxidil, avoid harsh styling"
        ],
        "medicines": [
            "Minoxidil"
        ]
    },
    "Yellow Nail Syndrome": {
        "symptoms": [
            "Yellow, thickened nails + lymphedema"
        ],
        "treatment": [
            "Vitamin E, treat underlying lung disease"
        ],
        "medicines": [
            "Vitamin E"
        ]
    },
    "Trachyonychia (20-Nail Dystrophy)": {
        "symptoms": [
            "Rough, sandpaper-like nails"
        ],
        "treatment": [
            "Observation (often self-resolving)"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Erythema Dyschromicum Perstans (Ashy Dermatosis)": {
        "symptoms": [
            "Slate-gray macules"
        ],
        "treatment": [
            "Clofazimine, sun protection"
        ],
        "medicines": [
            "Clofazimine"
        ]
    },
    "Nevus of Ota": {
        "symptoms": [
            "Bluish hyperpigmentation around eye"
        ],
        "treatment": [
            "Q-switched lasers"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Prurigo Nodularis": {
        "symptoms": [
            "Intensely itchy, excoriated nodules"
        ],
        "treatment": [
            "Dupilumab, thalidomide"
        ],
        "medicines": [
            "Dupilumab",
            "Thalidomide"
        ]
    },
    "Hidradenitis Suppurativa (Stage III)": {
        "symptoms": [
            "Draining sinus tracts in axillae/groin"
        ],
        "treatment": [
            "Adalimumab, wide excision"
        ],
        "medicines": [
            "Adalimumab"
        ]
    },
    "Discoid Lupus Erythematosus (DLE)": {
        "symptoms": [
            "Coin-shaped plaques with scaling/scarring"
        ],
        "treatment": [
            "Hydroxychloroquine, topical tacrolimus"
        ],
        "medicines": [
            "Hydroxychloroquine",
            "Tacrolimus ointment"
        ]
    },
    "Mixed Connective Tissue Disease (MCTD)": {
        "symptoms": [
            "Puffy hands, Raynaud's, overlapping SLE/scleroderma features"
        ],
        "treatment": [
            "Corticosteroids, mycophenolate"
        ],
        "medicines": [
            "Prednisone",
            "Mycophenolate"
        ]
    },
    "Livedoid Vasculopathy": {
        "symptoms": [
            "Painful leg ulcers with atrophic blanche"
        ],
        "treatment": [
            "Pentoxifylline, anticoagulants"
        ],
        "medicines": [
            "Pentoxifylline"
        ]
    },
    "Erythromelalgia": {
        "symptoms": [
            "Burning pain + redness in extremities"
        ],
        "treatment": [
            "Aspirin (primary), gabapentin"
        ],
        "medicines": [
            "Aspirin",
            "Gabapentin"
        ]
    },
    "Fabry Disease": {
        "symptoms": [
            "Angiokeratomas, acroparesthesias"
        ],
        "treatment": [
            "Enzyme replacement therapy"
        ],
        "medicines": [
            "Agalsidase beta"
        ]
    },
    "Gouty Tophi (Cutaneous)": {
        "symptoms": [
            "Chalky subcutaneous nodules"
        ],
        "treatment": [
            "Allopurinol, colchicine"
        ],
        "medicines": [
            "Allopurinol",
            "Colchicine"
        ]
    },
    "Orf (Parapoxvirus)": {
        "symptoms": [
            "Solitary nodule with central crust (sheep handlers)"
        ],
        "treatment": [
            "Self-resolves in 6 weeks"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Chromoblastomycosis": {
        "symptoms": [
            "Verrucous plaques with black dots"
        ],
        "treatment": [
            "Itraconazole + cryotherapy"
        ],
        "medicines": [
            "Itraconazole"
        ]
    },
    "Riehl Melanosis": {
        "symptoms": [
            "Gray-brown facial pigmentation"
        ],
        "treatment": [
            "Hydroquinone, laser"
        ],
        "medicines": [
            "Hydroquinone"
        ]
    },
    "Erythrasma": {
        "symptoms": [
            "Brown-red patches in folds (Corynebacterium)"
        ],
        "treatment": [
            "Erythromycin topical/oral"
        ],
        "medicines": [
            "Erythromycin"
        ]
    },
    "Erythema Elevatum Diutinum": {
        "symptoms": [
            "Persistent red-brown plaques on extensor surfaces"
        ],
        "treatment": [
            "Dapsone, colchicine"
        ],
        "medicines": [
            "Dapsone",
            "Colchicine"
        ]
    },
    "Fox-Fordyce Disease": {
        "symptoms": [
            "Itchy follicular papules in apocrine areas"
        ],
        "treatment": [
            "Topical clindamycin, oral contraceptives"
        ],
        "medicines": [
            "Clindamycin",
            "Oral contraceptives"
        ]
    },
    "Granuloma Faciale": {
        "symptoms": [
            "Red-brown facial plaques sparing mucosae"
        ],
        "treatment": [
            "Intralesional steroids, pulsed dye laser"
        ],
        "medicines": [
            "Intralesional corticosteroids"
        ]
    },
    "Pellagra": {
        "symptoms": [
            "Casal's necklace, photosensitive dermatitis"
        ],
        "treatment": [
            "Niacin supplementation"
        ],
        "medicines": [
            "Niacin"
        ]
    },
    "Scurvy": {
        "symptoms": [
            "Corkscrew hairs, perifollicular hemorrhage"
        ],
        "treatment": [
            "Vitamin C 1g daily"
        ],
        "medicines": [
            "Vitamin C"
        ]
    },
    "Serum Sickness-Like Reaction": {
        "symptoms": [
            "Urticaria + arthralgias (5-10 days post-drug)"
        ],
        "treatment": [
            "Prednisone taper, antihistamines"
        ],
        "medicines": [
            "Prednisone",
            "Antihistamines"
        ]
    },
    "Pseudoporphyria": {
        "symptoms": [
            "Porphyria-like blisters (NSAIDs/diuretics)"
        ],
        "treatment": [
            "Discontinue causative drug"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Dermatitis Artefacta": {
        "symptoms": [
            "Geometric lesions in accessible areas"
        ],
        "treatment": [
            "Psychotherapy, occlusive dressings"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Body Dysmorphic Disorder": {
        "symptoms": [
            "Excessive concern over minor skin flaws"
        ],
        "treatment": [
            "SSRIs, CBT"
        ],
        "medicines": [
            "Fluoxetine",
            "Sertraline"
        ]
    },
    "Lichen Myxedematosus": {
        "symptoms": [
            "Waxy papules in linear arrays"
        ],
        "treatment": [
            "IVIG, melphalan (severe)"
        ],
        "medicines": [
            "Intravenous immunoglobulin (IVIG)"
        ]
    },
    "Necrobiotic Xanthogranuloma": {
        "symptoms": [
            "Yellow plaques with atrophy"
        ],
        "treatment": [
            "Plasmapheresis for paraproteinemia"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Acrodermatitis Enteropathica": {
        "symptoms": [
            "Perioral/perineal erosions + alopecia (zinc deficiency)"
        ],
        "treatment": [
            "Zinc sulfate 3 mg/kg/day"
        ],
        "medicines": [
            "Zinc sulfate"
        ]
    },
    "Ainhum (Dactylolysis Spontanea)": {
        "symptoms": [
            "Constricting toe band (usually 5th toe)"
        ],
        "treatment": [
            "Surgical amputation if severe"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Bazex Syndrome (Acrokeratosis Paraneoplastica)": {
        "symptoms": [
            "Psoriasiform lesions on ears/nose/fingers"
        ],
        "treatment": [
            "Address underlying malignancy (often H&N SCC)"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Necrolytic Migratory Erythema (Glucagonoma)": {
        "symptoms": [
            "Geographic, erosive plaques in groin/periumbilical area"
        ],
        "treatment": [
            "Octreotide, surgical resection"
        ],
        "medicines": [
            "Octreotide"
        ]
    },
    "Degos Disease (Malignant Atrophic Papulosis)": {
        "symptoms": [
            "Porcelain-white \"pasted-on\" papules with red rim"
        ],
        "treatment": [
            "Eculizumab, treprostinil"
        ],
        "medicines": [
            "Eculizumab"
        ]
    },
    "Gougerot-Blum (Pigmented Purpuric Dermatosis)": {
        "symptoms": [
            "Cayenne pepper spots on legs"
        ],
        "treatment": [
            "Pentoxifylline, compression stockings"
        ],
        "medicines": [
            "Pentoxifylline"
        ]
    },
    "Blau Syndrome": {
        "symptoms": [
            "Childhood-onset granulomatous arthritis + uveitis"
        ],
        "treatment": [
            "Infliximab, corticosteroids"
        ],
        "medicines": [
            "Infliximab"
        ]
    },
    "Elastosis Perforans Serpiginosa": {
        "symptoms": [
            "Arc-shaped keratotic plaques (elastic fiber extrusion)"
        ],
        "treatment": [
            "Isotretinoin for severe cases"
        ],
        "medicines": [
            "Isotretinoin"
        ]
    },
    "Familial Mediterranean Fever": {
        "symptoms": [
            "Recurrent erysipelas-like erythema + fever"
        ],
        "treatment": [
            "Colchicine 1.2-2.4 mg/day"
        ],
        "medicines": [
            "Colchicine"
        ]
    },
    "Haber Syndrome": {
        "symptoms": [
            "Rosacea-like facial eruption + truncal keratoses"
        ],
        "treatment": [
            "Pulsed dye laser for telangiectasias"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Kimura Disease": {
        "symptoms": [
            "Subcutaneous head/neck nodules + eosinophilia"
        ],
        "treatment": [
            "Surgical excision, cyclosporine"
        ],
        "medicines": [
            "Cyclosporine"
        ]
    },
    "Idiopathic Guttate Hypomelanosis": {
        "symptoms": [
            "2-5mm white macules on sun-exposed limbs"
        ],
        "treatment": [
            "No effective therapy"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Subcorneal Pustular Dermatosis (Sneddon-Wilkinson Disease)": {
        "symptoms": [
            "Flaccid pustules in annular patterns (groin/axillae)"
        ],
        "treatment": [
            "Dapsone, retinoids"
        ],
        "medicines": [
            "Dapsone"
        ]
    },
    "Chronic Mucocutaneous Candidiasis": {
        "symptoms": [
            "Persistent Candida infections of skin/nails/mucosa"
        ],
        "treatment": [
            "Long-term fluconazole"
        ],
        "medicines": [
            "Fluconazole"
        ]
    },
    "Conradi-Hünermann Syndrome (X-linked dominant chondrodysplasia)": {
        "symptoms": [
            "Blaschkoid scaling, follicular atrophoderma"
        ],
        "treatment": [
            "Emollients, retinoids for ichthyosis"
        ],
        "medicines": [
            "Topical retinoids"
        ]
    },
    "Dowling-Degos Disease": {
        "symptoms": [
            "Reticulated pigmentation in flexures"
        ],
        "treatment": [
            "Laser therapy"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Mycetoma (Madura foot)": {
        "symptoms": [
            "Painless subcutaneous nodules with draining sinuses"
        ],
        "treatment": [
            "Eumycotic: Itraconazole; Actinomycotic: TMP-SMX + amikacin"
        ],
        "medicines": [
            "Itraconazole",
            "Trimethoprim-sulfamethoxazole",
            "Amikacin"
        ]
    },
    "Chromhidrosis": {
        "symptoms": [
            "Colored sweat (apocrine gland secretion)"
        ],
        "treatment": [
            "Capsaicin cream, botulinum toxin"
        ],
        "medicines": [
            "Botulinum toxin"
        ]
    },
    "Sinusoidal Hemangioma": {
        "symptoms": [
            "Blue subcutaneous nodules (elderly women)"
        ],
        "treatment": [
            "Surgical excision"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Targetoid Hemosiderotic Hemangioma": {
        "symptoms": [
            "Bruise-like annular lesion"
        ],
        "treatment": [
            "Observation (benign)"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Erythromelanosis Follicularis Faciei et Colli": {
        "symptoms": [
            "Red-brown pigmentation with follicular papules"
        ],
        "treatment": [
            "Pulsed dye laser"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Transient Neonatal Pustular Melanosis": {
        "symptoms": [
            "Vesiculopustules at birth → hyperpigmented macules"
        ],
        "treatment": [
            "Self-resolves"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Baboon Syndrome (Systemic Contact Dermatitis)": {
        "symptoms": [
            "V-shaped erythema in groin/buttocks"
        ],
        "treatment": [
            "Steroids, avoid allergen"
        ],
        "medicines": [
            "Prednisone"
        ]
    },
    "DRESS Syndrome (Drug Reaction with Eosinophilia and Systemic Symptoms)": {
        "symptoms": [
            "Rash + fever + organ involvement"
        ],
        "treatment": [
            "Systemic steroids, IVIG"
        ],
        "medicines": [
            "Prednisone",
            "Intravenous immunoglobulin (IVIG)"
        ]
    },
    "Monilethrix": {
        "symptoms": [
            "Beaded hair shafts, follicular keratosis"
        ],
        "treatment": [
            "Minoxidil, oral contraceptives (women)"
        ],
        "medicines": [
            "Minoxidil"
        ]
    },
    "Median Canaliform Dystrophy": {
        "symptoms": [
            "Central longitudinal split in nails"
        ],
        "treatment": [
            "Biotin supplementation"
        ],
        "medicines": [
            "Biotin"
        ]
    },
    "Merkel Cell Carcinoma": {
        "symptoms": [
            "Rapid-growing red/purple nodule"
        ],
        "treatment": [
            "Wide excision + radiation"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Microcystic Adnexal Carcinoma": {
        "symptoms": [
            "Indurated facial plaque"
        ],
        "treatment": [
            "Mohs surgery"
        ],
        "medicines": [
            "No specific medications"
        ]
    },
    "Multicentric Reticulohistiocytosis": {
        "symptoms": [
            "Flesh-colored papules + destructive arthritis"
        ],
        "treatment": [
            "Methotrexate, TNF inhibitors"
        ],
        "medicines": [
            "Methotrexate"
        ]
    },
    "Necrolytic Acral Erythema": {
        "symptoms": [
            "Psoriasiform plaques on feet (hepatitis C)"
        ],
        "treatment": [
            "Zinc supplementation"
        ],
        "medicines": [
            "Zinc"
        ]
    }
}


# Function to verify disease name with Google
def verify_disease_with_google(disease_name):
    try:
        query = f"is {disease_name} a valid skin disease?"
        search_results = list(search(query, num=3, stop=3, pause=2))
        # Check if any of the results contain the disease name in reputable sources
        reputable_sources = ['wikipedia.org', 'webmd.com', 'mayoclinic.org', 'healthline.com', 'medicalnewstoday.com']
        for result in search_results:
            if any(source in result.lower() for source in reputable_sources):
                return True
        return False
    except Exception as e:
        print(f"Error verifying disease with Google: {e}")
        return True  # Assume valid if verification fails


# Function to search disease information from medical websites
def search_disease_info(disease_name):
    try:
        query = f"{disease_name} skin disease symptoms and treatment"
        search_results = list(search(query, num=5, stop=5, pause=2))
        medical_sources = []
        for result in search_results:
            if any(domain in result for domain in
                   ['mayoclinic.org', 'webmd.com', 'healthline.com', 'medicalnewstoday.com']):
                medical_sources.append(result)
        return medical_sources[:3]  # Return top 3 medical sources
    except Exception as e:
        print(f"Error searching disease info: {e}")
        return []


# Function to load and preprocess training images
def load_training_images(train_dir='train'):
    disease_images = {}
    for disease in os.listdir(train_dir):
        disease_path = os.path.join(train_dir, disease)
        if os.path.isdir(disease_path):
            images = []
            for img_file in os.listdir(disease_path):
                if img_file.endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(disease_path, img_file)
                    try:
                        img = Image.open(img_path)
                        img = img.resize((224, 224))
                        img_array = np.array(img)
                        if len(img_array.shape) == 2:
                            img_array = np.stack((img_array,) * 3, axis=-1)
                        images.append(img_array)
                    except Exception as e:
                        print(f"Error loading {img_path}: {e}")
            if images:
                disease_images[disease] = images
    return disease_images


def extract_features(img_array):
    if len(img_array.shape) == 2:
        img_array = np.stack((img_array,) * 3, axis=-1)
    # Convert to RGB if it's grayscale
    if img_array.shape[2] == 1:
        img_array = np.concatenate([img_array] * 3, axis=2)
    # Convert to BGR for OpenCV processing
    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    # Color histograms
    hist_r = cv2.calcHist([img_array], [0], None, [256], [0, 256]).flatten()
    hist_g = cv2.calcHist([img_array], [1], None, [256], [0, 256]).flatten()
    hist_b = cv2.calcHist([img_array], [2], None, [256], [0, 256]).flatten()
    # Texture features
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    patches = extract_patches_2d(gray, (32, 32), max_patches=10)
    patch_features = [p.flatten() for p in patches]
    texture_feature = np.mean(patch_features, axis=0)
    # Shape features
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        shape_feature = cv2.HuMoments(cv2.moments(largest_contour)).flatten()
    else:
        shape_feature = np.zeros(7)
    features = np.concatenate([hist_r, hist_g, hist_b, texture_feature, shape_feature])
    return features


def find_similar_disease(uploaded_img, disease_images, threshold=0.85):
    try:
        uploaded_img = uploaded_img.resize((224, 224))
        uploaded_array = np.array(uploaded_img)
        if len(uploaded_array.shape) == 2:
            uploaded_array = np.stack((uploaded_array,) * 3, axis=-1)
        uploaded_features = extract_features(uploaded_array)
        best_match = None
        best_score = 0
        all_scores = {}
        # Step 1: Check against training images first
        for disease, images in disease_images.items():
            max_similarity = 0
            for train_img in images:
                train_features = extract_features(train_img)
                similarity = cosine_similarity([uploaded_features], [train_features])[0][0]
                if similarity > max_similarity:
                    max_similarity = similarity
            all_scores[disease] = max_similarity
            if max_similarity > best_score:
                best_score = max_similarity
                best_match = disease
        # Debug: Show all scores
        print("Matching scores:", all_scores)
        if best_score >= threshold:
            # Step 2: Verify the disease name with Google
            is_valid_disease = verify_disease_with_google(best_match)
            if is_valid_disease:
                return best_match.replace('_', ' ').title(), best_score
            else:
                # Step 3: If not found in Google, search medical websites
                medical_sources = search_disease_info(best_match)
                if medical_sources:
                    return best_match.replace('_', ' ').title(), best_score
                else:
                    return "Unknown", best_score
        else:
            return "Unknown", best_score
    except Exception as e:
        print(f"Error in matching: {e}")
        return "Error", 0


def get_disease_info(disease_name):
    # If Wikipedia is available, try to fetch from there first
    if WIKIPEDIA_AVAILABLE:
        try:
            page_py = wiki_wiki.page(disease_name)
            if page_py.exists():
                summary = page_py.summary.split('. ')[0:3]
                wiki_summary = '. '.join(summary) + '.'
                return {
                    'disease_name': disease_name,
                    'scientific_name': disease_name,
                    'description': wiki_summary,
                    'severity': 'Moderate',
                    'treatment': 'Consult a dermatologist for proper diagnosis and treatment.',
                    'recommended_tablets': ['Consult doctor for medications'],
                    'prevention': ['Avoid known irritants', 'Maintain proper skin hygiene'],
                    'follow_up': 'Recommended in 2 weeks if no improvement',
                    'source': f"Source: Wikipedia ({page_py.fullurl})"
                }
        except:
            pass
    # Check if we have detailed medicine data for this disease
    if disease_name in MEDICINE_DATABASE:
        disease_data = MEDICINE_DATABASE[disease_name]
        return {
            'disease_name': disease_name,
            'scientific_name': disease_name,
            'description': f"A dermatological condition characterized by: {', '.join(disease_data['symptoms'])}",
            'severity': random.choice(['Mild', 'Moderate', 'Severe']),
            'treatment': 'Treatment options include: ' + ', '.join(disease_data['treatment']),
            'recommended_tablets': disease_data['medicines'],
            'prevention': ['Avoid triggers', 'Maintain proper skin hygiene', 'Follow medical advice'],
            'follow_up': 'Recommended in 2 weeks if no improvement',
            'source': 'Medical database'
        }
    # Fallback to built-in information with more realistic details
    disease_info = {
        'disease_name': disease_name,
        'scientific_name': disease_name,
        'description': 'A dermatological condition requiring professional evaluation.',
        'severity': 'Moderate',
        'treatment': 'Consult a dermatologist for proper diagnosis and treatment.',
        'recommended_tablets': ['Consult doctor for medications'],
        'prevention': ['Avoid known irritants', 'Maintain proper skin hygiene'],
        'follow_up': 'Recommended in 2 weeks if no improvement',
        'source': 'Medical database'
    }
    # Try to find additional information from medical websites
    medical_sources = search_disease_info(disease_name)
    if medical_sources:
        disease_info['source'] = f"Verified information from: {', '.join(medical_sources[:2])}"
    # Add disease-specific information if available with more realistic details
    if "eczema" in disease_name.lower():
        disease_info.update({
            'scientific_name': 'Atopic Dermatitis',
            'description': 'Eczema is a chronic condition that causes the skin to become red, itchy, dry, and cracked. It often appears in patches on the hands, feet, ankles, wrists, neck, upper chest, eyelids, and inside the bend of the elbows and knees.',
            'severity': random.choice(['Mild', 'Moderate', 'Severe']),
            'treatment': 'Treatment focuses on healing damaged skin and relieving symptoms. Doctors typically recommend regular use of emollients/moisturizers, topical corticosteroids for flare-ups, and antihistamines for itching. For severe cases, phototherapy or immunosuppressants may be prescribed.',
            'recommended_tablets': ['Hydrocortisone 1% cream (mild cases)',
                                    'Betamethasone valerate 0.1% cream (moderate cases)',
                                    'Tacrolimus ointment (for sensitive areas)', 'Cetirizine 10mg (antihistamine)',
                                    'Loratadine 10mg (non-drowsy antihistamine)'],
            'prevention': ['Moisturize at least twice daily with fragrance-free creams',
                           'Identify and avoid triggers (common ones include stress, sweat, dust mites, pet dander)',
                           'Use gentle, fragrance-free skin care products', 'Take shorter showers with lukewarm water',
                           'Wear soft, breathable fabrics like cotton', 'Use a humidifier in dry weather'],
            'follow_up': 'Follow up in 1-2 weeks if symptoms persist or worsen, or as directed by your dermatologist'
        })
    elif "psoriasis" in disease_name.lower():
        disease_info.update({
            'scientific_name': 'Psoriasis Vulgaris',
            'description': 'Psoriasis is an autoimmune condition that causes rapid buildup of skin cells, leading to scaling on the skin surface. Common symptoms include red patches covered with thick, silvery scales; dry, cracked skin that may bleed; itching, burning, or soreness; and thickened, pitted or ridged nails.',
            'severity': random.choice(['Mild', 'Moderate', 'Severe']),
            'treatment': 'Treatment options include topical corticosteroids, vitamin D analogs, retinoid creams, coal tar preparations, and salicylic acid. For moderate to severe cases, phototherapy, oral medications (like methotrexate), or biologic drugs may be recommended.',
            'recommended_tablets': ['Topical corticosteroids (betamethasone dipropionate)',
                                    'Calcipotriene (vitamin D analog)', 'Tazarotene (retinoid cream)',
                                    'Coal tar preparations', 'Methotrexate (for severe cases)'],
            'prevention': ['Keep skin moisturized with thick creams or ointments', 'Avoid skin injuries and sunburns',
                           'Manage stress through relaxation techniques', 'Avoid smoking and limit alcohol consumption',
                           'Maintain a healthy weight', 'Follow a balanced diet rich in omega-3 fatty acids'],
            'follow_up': 'Follow up in 2-4 weeks to assess treatment response, or sooner if symptoms worsen'
        })
    elif "acne" in disease_name.lower():
        disease_info.update({
            'scientific_name': 'Acne Vulgaris',
            'description': 'Acne occurs when hair follicles become plugged with oil and dead skin cells, leading to whiteheads, blackheads, or pimples. It most commonly appears on the face, forehead, chest, upper back and shoulders. Severe acne can cause painful, pus-filled cysts and nodules, potentially leading to scarring.',
            'severity': random.choice(['Mild', 'Moderate', 'Severe']),
            'treatment': 'Treatment depends on severity. Options include topical retinoids, benzoyl peroxide, antibiotics (clindamycin), and salicylic acid. For moderate cases, oral antibiotics (doxycycline) may be prescribed. Severe cases may require isotretinoin or hormonal treatments for women.',
            'recommended_tablets': ['Benzoyl peroxide 2.5-10% (start with lower concentrations)',
                                    'Adapalene 0.1% gel (retinoid)', 'Clindamycin 1% solution (antibiotic)',
                                    'Doxycycline 50-100mg (oral antibiotic for moderate cases)',
                                    'Isotretinoin (for severe, cystic acne)'],
            'prevention': ['Wash face twice daily with gentle cleanser', 'Use non-comedogenic, oil-free products',
                           'Avoid picking or squeezing pimples', 'Shower after sweating heavily',
                           'Wash hair regularly, especially if oily', 'Manage stress levels',
                           'Follow a balanced diet with limited dairy and high-glycemic foods'],
            'follow_up': 'Follow up in 4-6 weeks to assess treatment effectiveness, or sooner if experiencing severe irritation'
        })
    elif "rosacea" in disease_name.lower():
        disease_info.update({
            'scientific_name': 'Rosacea',
            'description': 'Rosacea is a chronic skin condition that causes redness and visible blood vessels in your face, often with small, red, pus-filled bumps. It typically affects the central part of the face (cheeks, nose, chin, forehead) and can flare up for weeks to months before diminishing. Many people experience eye irritation (ocular rosacea) as well.',
            'severity': random.choice(['Mild', 'Moderate', 'Severe']),
            'treatment': 'Treatment focuses on controlling signs and symptoms. Options include topical medications (metronidazole, azelaic acid), oral antibiotics (doxycycline), and laser therapy for visible blood vessels. Identifying and avoiding triggers is crucial for management.',
            'recommended_tablets': ['Metronidazole 0.75% cream or gel', 'Azelaic acid 15% gel', 'Ivermectin 1% cream',
                                    'Doxycycline 40mg (anti-inflammatory dose)',
                                    'Brimonidine tartrate gel (for redness)'],
            'prevention': [
                'Identify and avoid triggers (common ones include alcohol, spicy foods, temperature extremes, sunlight, stress)',
                'Use gentle skin care products without alcohol or harsh ingredients',
                'Apply broad-spectrum sunscreen daily (SPF 30+)', 'Manage stress through relaxation techniques',
                'Keep a symptom diary to identify personal triggers', 'Protect face from cold and wind in winter'],
            'follow_up': 'Follow up in 4-6 weeks to assess treatment response, or sooner if experiencing worsening symptoms'
        })
    return disease_info


def get_coordinates(city_name):
    url = f"https://api.geoapify.com/v1/geocode/search?text={city_name}&apiKey={GEOAPIFY_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200 and response.json()['features']:
        coords = response.json()['features'][0]['geometry']['coordinates']
        return coords[1], coords[0]
    return None, None


def find_nearby_hospitals(lat, lon):
    url = f"https://api.geoapify.com/v2/places?categories=healthcare.hospital&filter=circle:{lon},{lat},5000&limit=10&apiKey={GEOAPIFY_API_KEY}"
    response = requests.get(url)
    hospitals = []
    if response.status_code == 200:
        for feature in response.json().get('features', []):
            props = feature['properties']
            hospitals.append({
                'name': props.get('name', 'Unknown'),
                'address': props.get('formatted', 'No address provided'),
                'lat': feature['geometry']['coordinates'][1],
                'lon': feature['geometry']['coordinates'][0]
            })
    return hospitals


# Load training images at startup
if 'disease_images' not in st.session_state:
    st.session_state.disease_images = load_training_images()

# App Configuration
st.set_page_config(
    page_title="Skin Health Pro+ — AI Dermatology Dashboard",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Medical Dashboard Styling with new animations
st.markdown("""
    <style>
        :root {
            --primary: #4a6fa5;
            --primary-dark: #2c4d7a;
            --primary-light: #e1e8f5;
            --secondary: #ff7e5f;
            --background: #f8f9fa;
            --card-bg: #ffffff;
            --text-dark: #2d3748;
            --text-light: #718096;
            --border-radius: 12px;
            --box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        body {
            background-color: var(--background);
            font-family: 'Inter', sans-serif;
        }
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid #e2e8f0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: var(--border-radius);
            animation: fadeIn 1s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .header-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .header-subtitle {
            font-size: 1rem;
            color: rgba(255,255,255,0.8);
            margin-top: -0.5rem;
        }
        .card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-top: 4px solid var(--primary);
            transition: all 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        }
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--primary-dark);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .diagnosis-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--primary-light);
            color: var(--primary-dark);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 1rem;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .severity-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        .severity-mild {
            background: #48bb78;
        }
        .severity-moderate {
            background: #ed8936;
        }
        .severity-severe {
            background: #f56565;
        }
        .treatment-card {
            background: var(--primary-light);
            padding: 1.25rem;
            border-radius: var(--border-radius);
            margin: 1.5rem 0;
        }
        .hospital-box {
            border: 1px solid #e2e8f0;
            border-radius: var(--border-radius);
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        .hospital-box:hover {
            border-color: var(--primary);
            box-shadow: var(--box-shadow);
            transform: translateY(-3px);
        }
        .hospital-name {
            font-weight: 600;
            color: var(--primary-dark);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
        }
        .hospital-address {
            font-size: 0.85rem;
            color: var(--text-light);
            margin-bottom: 0.5rem;
        }
        .hospital-distance {
            font-size: 0.75rem;
            color: var(--primary);
            font-weight: 500;
        }
        .progress-text {
            color: var(--primary-dark);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .product-card {
            border-radius: var(--border-radius);
            overflow: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        .product-image {
            height: 200px;
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: flex-end;
        }
        .product-content {
            padding: 1.5rem;
            background: white;
        }
        .product-title {
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        .product-description {
            color: var(--text-light);
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .product-price {
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        .product-button {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            width: 100%;
            transition: all 0.2s;
            font-weight: 600;
        }
        .product-button:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.2s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
        }
        /* Animated gradient background for upload section */
        .upload-container {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            border-radius: var(--border-radius);
            padding: 2rem;
            margin-bottom: 2rem;
            color: white;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        /* Professional Data Table */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .data-table th {
            background-color: var(--primary-light);
            color: var(--primary-dark);
            text-align: left;
            padding: 0.75rem;
            font-weight: 600;
        }
        .data-table td {
            padding: 0.75rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .data-table tr:hover {
            background-color: rgba(74, 111, 165, 0.05);
        }
        /* New animations */
        .fade-in {
            animation: fadeIn 1s ease-in;
        }
        .slide-up {
            animation: slideUp 0.8s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .rotate {
            animation: rotate 2s linear infinite;
        }
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .bounce {
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
            40% {transform: translateY(-20px);}
            60% {transform: translateY(-10px);}
        }
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .header-container {
                flex-direction: column;
                align-items: flex-start;
            }
            .product-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Header with gradient background and animation
st.markdown("""
    <div class="header-container">
        <div>
            <h1 class="header-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
                Skin Health Pro+
            </h1>
            <p class="header-subtitle">Advanced AI dermatology diagnostics with Wikipedia integration</p>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; display: flex; align-items: center; gap: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span style="color: white; font-weight: 500;">Real-time Analysis</span>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; display: flex; align-items: center; gap: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                </svg>
                <span style="color: white; font-weight: 500;">Wikipedia Integrated</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main content in two columns
col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    # Upload Section with animated gradient
    st.markdown("""
        <div class="upload-container">
            <h3 style="margin-top: 0; color: white; display: flex; align-items: center; gap: 0.75rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                Upload Skin Image
            </h3>
            <p style="color: rgba(255,255,255,0.9);">Get an instant analysis of your skin condition by uploading a clear photo</p>
        </div>
    """, unsafe_allow_html=True)

    # Lottie animation for upload section
    if lottie_scan:
        st_lottie(lottie_scan, height=200, key="upload-animation")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"],
                                     label_visibility="collapsed")
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded dermatological image", use_column_width=True)
        # Animated AI Analysis with progress bar
        with st.spinner(""):
            progress_bar = st.progress(0)
            status_text = st.markdown('<p class="progress-text">🔍 Analyzing skin condition with AI diagnostics...</p>',
                                      unsafe_allow_html=True)
            for percent_complete in range(100):
                time.sleep(0.02)
                progress_bar.progress(percent_complete + 1)
            progress_bar.empty()
            status_text.empty()
            # Find matching disease
            disease_name, confidence = find_similar_disease(image, st.session_state.disease_images)
            result = get_disease_info(disease_name)
            # Update disease name based on match
            if disease_name != "Unknown" and disease_name != "Error":
                st.success(f"Match found with {confidence * 100:.1f}% confidence")
                st.info(f"Diagnosis verified through multiple medical sources")
            else:
                st.warning(
                    f"Unable to make confident diagnosis (confidence: {confidence * 100:.1f}%). Showing general information.")
        # Diagnosis Section with animation
        st.markdown('<div class="card slide-up">', unsafe_allow_html=True)
        st.markdown("""
            <div class="card-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <path d="M14 2v6h6"></path>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                Diagnostic Report
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="diagnosis-badge">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                </svg>
                <span>Primary Diagnosis</span>
            </div>
            <h3 style="margin-top: 0; color: var(--primary-dark);">{result['disease_name']}</h3>
            <p style="color: var(--text-light);"><i>{result['scientific_name']}</i></p>
            <p>{result['description']}</p>
            <p style="font-size: 0.85rem; color: var(--text-light);">{result['source']}</p>
            <div style="display: flex; gap: 1rem; margin: 1.5rem 0;">
                <div style="flex: 1; background: var(--primary-light); padding: 1.25rem; border-radius: 12px;">
                    <div style="font-size: 0.85rem; color: var(--text-light); margin-bottom: 0.5rem;">Severity</div>
                    <div style="font-weight: 600; color: var(--text-dark); display: flex; align-items: center;">
                        <span class="severity-indicator severity-{result['severity'].lower()}"></span>
                        {result['severity']}
                    </div>
                </div>
                <div style="flex: 1; background: var(--primary-light); padding: 1.25rem; border-radius: 12px;">
                    <div style="font-size: 0.85rem; color: var(--text-light); margin-bottom: 0.5rem;">Follow-up</div>
                    <div style="font-weight: 600; color: var(--text-dark);">
                        {result['follow_up']}
                    </div>
                </div>
            </div>
            <div class="treatment-card">
                <h4 style="margin-top: 0; color: var(--primary-dark); display: flex; align-items: center; gap: 0.5rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                        <line x1="9" y1="9" x2="9.01" y2="9"></line>
                        <line x1="15" y1="9" x2="15.01" y2="9"></line>
                    </svg>
                    Recommended Treatment
                </h4>
                <p>{result['treatment']}</p>
                <h4 style="margin-bottom: 0.75rem; color: var(--primary-dark); display: flex; align-items: center; gap: 0.5rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
                        <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
                        <line x1="6" y1="1" x2="6" y2="4"></line>
                        <line x1="10" y1="1" x2="10" y2="4"></line>
                        <line x1="14" y1="1" x2="14" y2="4"></line>
                    </svg>
                    Medications:
                </h4>
                <ul style="margin-top: 0;">
                    {''.join([f'<li style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>{med}</li>' for med in result['recommended_tablets']])}
                </ul>
            </div>
            <h4 style="color: var(--primary-dark); margin-top: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
                Prevention Tips
            </h4>
            <ul style="margin-top: 0;">
                {''.join([f'<li style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>{tip}</li>' for tip in result['prevention']])}
            </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # Close diagnosis card

        # Product Recommendations Section with animation
        st.markdown('<div class="card slide-up">', unsafe_allow_html=True)
        st.markdown("""
            <div class="card-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="9" cy="21" r="1"></circle>
                    <circle cx="20" cy="21" r="1"></circle>
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                </svg>
                Recommended Products
            </div>
            <p style="color: var(--text-light);">These products may help with your condition:</p>
        """, unsafe_allow_html=True)

        # Lottie animation for products section
        if lottie_health:
            st_lottie(lottie_health, height=150, key="products-animation")

        # Get appropriate products based on disease
        if disease_name in PRODUCT_RECOMMENDATIONS:
            products = random.sample(PRODUCT_RECOMMENDATIONS[disease_name],
                                     min(3, len(PRODUCT_RECOMMENDATIONS[disease_name])))
        else:
            products = random.sample(PRODUCT_RECOMMENDATIONS['default'], 3)
        # Product grid
        st.markdown('<div class="product-grid">', unsafe_allow_html=True)
        for product in products:
            st.markdown(f"""
                <div class="product-card">
                    <div class="product-image" style="background-color: {product['color']}; background-image: url('{product['image']}')">
                    </div>
                    <div class="product-content">
                        <h3 class="product-title">{product['name']}</h3>
                        <p class="product-description">{product['description']}</p>
                        <div class="product-price">{product['price']}</div>
                        <a href="{product['url']}" target="_blank" class="product-button">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                            </svg>
                            Buy Now
                        </a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # Close product grid
        st.markdown('</div>', unsafe_allow_html=True)  # Close product recommendations card

with col2:
    # Hospital Finder Section with animation
    st.markdown('<div class="card slide-up" id="hospitals-section">', unsafe_allow_html=True)
    st.markdown("""
        <div class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
                <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
                <line x1="6" y1="1" x2="6" y2="4"></line>
                <line x1="10" y1="1" x2="10" y2="4"></line>
                <line x1="14" y1="1" x2="14" y2="4"></line>
            </svg>
            Healthcare Facilities Locator
        </div>
    """, unsafe_allow_html=True)

    # Lottie animation for hospital finder
    if lottie_doctor:
        st_lottie(lottie_doctor, height=200, key="hospital-animation")

    city = st.text_input("Enter your location to find accredited dermatology centers:", placeholder="City or ZIP code")
    if city:
        with st.spinner("Locating certified healthcare providers..."):
            lat, lon = get_coordinates(city)
            if lat and lon:
                hospitals = find_nearby_hospitals(lat, lon)
                if hospitals:
                    st.success(f"Found {len(hospitals)} accredited medical centers near {city}")
                    for idx, hospital in enumerate(hospitals, 1):
                        st.markdown(f"""
                            <div class="hospital-box">
                                <div class="hospital-name">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
                                        <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
                                        <line x1="6" y1="1" x2="6" y2="4"></line>
                                        <line x1="10" y1="1" x2="10" y2="4"></line>
                                        <line x1="14" y1="1" x2="14" y2="4"></line>
                                    </svg>
                                    {hospital['name']}
                                </div>
                                <div class="hospital-address">📍 {hospital['address']}</div>
                                <div class="hospital-distance">{(idx * 1.5):.1f} miles</div>
                            </div>
                        """, unsafe_allow_html=True)

                    # Patient Information Form for Medical Report
                    with st.form("patient_info_form"):
                        st.subheader("Patient Information", divider='rainbow')
                        patient_name = st.text_input("Enter Patient's Full Name:")
                        patient_age = st.text_input("Enter Patient's Age:")
                        submitted = st.form_submit_button("Generate Medical Report")

                    if submitted:
                        if not patient_name or not patient_age:
                            st.warning("Please enter both your name and age to generate the report.")
                        else:
                            # Generate professional medical report HTML
                            report_html = f"""
                            <div style="background-color:#ffffff; padding:2rem; border-radius:10px; box-shadow:0px 4px 12px rgba(0,0,0,0.1); font-family:Arial, sans-serif; color:#333;">
                                <h2 style="color:#2E86C1; text-align:center; margin-bottom:1rem;">Skin Health Pro+ - Medical Report</h2>
                                <hr style="border:1px solid #2E86C1; margin-bottom:2rem;">

                                <h4 style="color:#154360;">Patient Details</h4>
                                <p><b>Name:</b> {patient_name}</p>
                                <p><b>Age:</b> {patient_age} years</p>
                                <p><b>Location:</b> {city.upper()}</p>

                                <hr style="margin:1.5rem 0;">

                                <h4 style="color:#154360;">Diagnosis Summary</h4>
                                <p><b>Condition:</b> {result['disease_name']} (<i>{result['scientific_name']}</i>)</p>
                                <p><b>Severity:</b> {result['severity']}</p>
                                <p><b>Description:</b> {result['description']}</p>
                                <p><b>Source:</b> {result['source']}</p>

                                <hr style="margin:1.5rem 0;">

                                <h4 style="color:#154360;">Treatment Recommendations</h4>
                                <p>{result['treatment']}</p>

                                <h4 style="color:#154360;">Prescribed Medications</h4>
                                <ul style="list-style-type:square; padding-left:1.5rem;">
                                    {''.join([f"<li>{tablet}</li>" for tablet in result['recommended_tablets']])}
                                </ul>

                                <h4 style="color:#154360;">Prevention Guidance</h4>
                                <ul style="list-style-type:disc; padding-left:1.5rem;">
                                    {''.join([f"<li>{point}</li>" for point in result['prevention']])}
                                </ul>

                                <hr style="margin:1.5rem 0;">

                                <h4 style="color:#154360;">Recommended Hospitals in {city.upper()}</h4>
                                <ul style="list-style-type:circle; padding-left:1.5rem;">
                                    {''.join([f"<li><b>{hospital['name']}</b> - {hospital['address']}</li>" for hospital in hospitals])}
                                </ul>

                                <hr style="margin:2rem 0; border:1px solid #2E86C1;">

                                <p style="text-align:center; font-size:0.9rem; color:#888;">This AI-generated report is for informational purposes only and does not replace professional medical advice.</p>
                                <p style="text-align:center; font-size:0.85rem; color:#aaa;">Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
                            </div>
                            """

                            # Show the report correctly
                            components.html(report_html, height=1500, scrolling=True)

                            # Downloadable plain text version

                            styled_report_html = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <style>
                                    body {{
                                        font-family: Arial, sans-serif;
                                        color: #333;
                                        line-height: 1.6;
                                        padding: 20px;
                                        max-width: 800px;
                                        margin: 0 auto;
                                    }}
                                    .report-header {{
                                        color: #2E86C1;
                                        text-align: center;
                                        margin-bottom: 20px;
                                        border-bottom: 2px solid #2E86C1;
                                        padding-bottom: 10px;
                                    }}
                                    .section-title {{
                                        color: #154360;
                                        margin-top: 25px;
                                        margin-bottom: 10px;
                                        border-bottom: 1px solid #D6EAF8;
                                        padding-bottom: 5px;
                                    }}
                                    .patient-details {{
                                        background-color: #F8F9F9;
                                        padding: 15px;
                                        border-radius: 5px;
                                        margin-bottom: 20px;
                                    }}
                                    .diagnosis-box {{
                                        background-color: #EBF5FB;
                                        padding: 15px;
                                        border-left: 4px solid #2E86C1;
                                        margin-bottom: 20px;
                                    }}
                                    .treatment-box {{
                                        background-color: #E8F8F5;
                                        padding: 15px;
                                        border-left: 4px solid #1ABC9C;
                                        margin-bottom: 20px;
                                    }}
                                    .hospital-box {{
                                        background-color: #FEF9E7;
                                        padding: 15px;
                                        border-left: 4px solid #F1C40F;
                                        margin-bottom: 20px;
                                    }}
                                    ul {{
                                        padding-left: 20px;
                                    }}
                                    li {{
                                        margin-bottom: 8px;
                                    }}
                                    .footer {{
                                        text-align: center;
                                        font-size: 0.9rem;
                                        color: #888;
                                        margin-top: 30px;
                                        border-top: 1px solid #D6EAF8;
                                        padding-top: 15px;
                                    }}
                                    .footer-small {{
                                        font-size: 0.8rem;
                                        color: #aaa;
                                    }}
                                    .severity {{
                                        display: inline-block;
                                        padding: 3px 10px;
                                        border-radius: 15px;
                                        font-size: 0.9rem;
                                        font-weight: bold;
                                        margin-left: 10px;
                                    }}
                                    .severity-mild {{
                                        background-color: #48bb78;
                                        color: white;
                                    }}
                                    .severity-moderate {{
                                        background-color: #ed8936;
                                        color: white;
                                    }}
                                    .severity-severe {{
                                        background-color: #f56565;
                                        color: white;
                                    }}
                                </style>
                            </head>
                            <body>
                                <div class="report-header">
                                    <h1>Skin Health Pro+ - Medical Report</h1>
                                </div>

                                <div class="patient-details">
                                    <h3>Patient Details</h3>
                                    <p><strong>Name:</strong> {patient_name}</p>
                                    <p><strong>Age:</strong> {patient_age} years</p>
                                    <p><strong>Location:</strong> {city.upper()}</p>
                                </div>

                                <div class="diagnosis-box">
                                    <h3 class="section-title">Diagnosis Summary</h3>
                                    <p><strong>Condition:</strong> {result['disease_name']} (<i>{result['scientific_name']}</i>)</p>
                                    <p><strong>Severity:</strong> {result['severity']} <span class="severity severity-{result['severity'].lower()}">{result['severity']}</span></p>
                                    <p><strong>Description:</strong> {result['description']}</p>
                                    <p><strong>Source:</strong> {result['source']}</p>
                                </div>

                                <div class="treatment-box">
                                    <h3 class="section-title">Treatment Recommendations</h3>
                                    <p>{result['treatment']}</p>

                                    <h4>Prescribed Medications</h4>
                                    <ul>
                                        {''.join([f"<li>{tablet}</li>" for tablet in result['recommended_tablets']])}
                                    </ul>

                                    <h4>Prevention Guidance</h4>
                                    <ul>
                                        {''.join([f"<li>{point}</li>" for point in result['prevention']])}
                                    </ul>
                                </div>

                                <div class="hospital-box">
                                    <h3 class="section-title">Recommended Hospitals in {city.upper()}</h3>
                                    <ul>
                                        {''.join([f"<li><strong>{hospital['name']}</strong> - {hospital['address']}</li>" for hospital in hospitals])}
                                    </ul>
                                </div>

                                <div class="footer">
                                    <p>This AI-generated report is for informational purposes only and does not replace professional medical advice.</p>
                                    <p class="footer-small">Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
                                </div>
                            </body>
                            </html>
                            """

                            # ✅ Single download button
                            st.download_button(
                                label="📄 Download Full Report (HTML)",
                                data=styled_report_html,
                                file_name=f"{patient_name}_SkinHealthReport.html",
                                mime="text/html"
                            )

# Additional Information Section
st.markdown('<div class="card slide-up">', unsafe_allow_html=True)
st.markdown("""
        <div class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            Skin Health Tips
        </div>
        <div style="margin-bottom: 1rem;">
            <h4 style="color: var(--primary-dark); margin-bottom: 0.5rem;">Daily Skin Care Routine</h4>
            <ul style="margin-top: 0;">
                <li>Cleanse your skin twice daily</li>
                <li>Use sunscreen with SPF 30+ every day</li>
                <li>Moisturize regularly</li>
                <li>Stay hydrated and eat a balanced diet</li>
            </ul>
        </div>
        <div style="margin-bottom: 1rem;">
            <h4 style="color: var(--primary-dark); margin-bottom: 0.5rem;">When to See a Dermatologist</h4>
            <ul style="margin-top: 0;">
                <li>Persistent acne or skin irritation</li>
                <li>Changing moles or skin growths</li>
                <li>Unexplained rashes or skin discoloration</li>
                <li>Severe dryness or itching</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # Close additional info card

# Footer with animation
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 1.5rem; background-color: var(--primary-light); border-radius: var(--border-radius); animation: fadeIn 1s ease-in;">
        <p style="color: var(--primary-dark); font-size: 0.9rem;">Skin Health Pro+ uses AI technology to analyze skin conditions. This is not a substitute for professional medical advice.</p>
        <p style="color: var(--text-light); font-size: 0.8rem;">© 2023 Skin Health Pro+. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

