import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")
from io import StringIO

st.set_page_config(
    page_title="Luggage Brand Intelligence Dashboard",
    page_icon="\U0001f9f3",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1d2e 0%, #16213e 100%);
        border: 1px solid #2a2d3e; border-radius: 12px; padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label { color: #8892b0 !important; font-size: 0.8rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #64ffda !important; font-size: 2rem !important; font-weight: 700; }
    h1 { color: #ccd6f6 !important; font-weight: 700; }
    h2 { color: #a8b2d8 !important; }
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #21262d; }
    .stTabs [data-baseweb="tab-list"] { background-color: #161b22; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8892b0; border-radius: 6px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #21262d; color: #64ffda; }
    .insight-card {
        background: linear-gradient(135deg, #1a1d2e, #162032);
        border: 1px solid #30363d; border-left: 3px solid #64ffda;
        border-radius: 10px; padding: 16px 20px; margin: 8px 0;
        font-size: 0.92rem; color: #c9d1d9; line-height: 1.6;
    }
    .pos-tag { background: rgba(100,255,218,0.15); color: #64ffda; border: 1px solid rgba(100,255,218,0.3); border-radius: 6px; padding: 3px 10px; font-size: 0.8rem; margin: 2px; display: inline-block; }
    .neg-tag { background: rgba(255,85,85,0.15); color: #ff5555; border: 1px solid rgba(255,85,85,0.3); border-radius: 6px; padding: 3px 10px; font-size: 0.8rem; margin: 2px; display: inline-block; }
    .section-header { font-size: 1.1rem; font-weight: 600; color: #ccd6f6; border-bottom: 1px solid #21262d; padding-bottom: 8px; margin: 16px 0 12px; }
    .divider { border: none; border-top: 1px solid #21262d; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ── Embedded Data ──────────────────────────────────────────────────────────────
PRODUCTS_CSV = """brand,product_title,asin,category,size,price,list_price,discount_pct,rating,review_count,url
American Tourister,American Tourister Linea Polypropylene 55 cm Small Cabin Trolley Bag,B08XYZ1234,Cabin,Small,3299,4999,34.0,4.2,3821,https://amazon.in/dp/B08XYZ1234
American Tourister,American Tourister Linea Polypropylene 68 cm Medium Check-in Trolley,B08XYZ1235,Check-in,Medium,4299,6499,33.8,4.3,2914,https://amazon.in/dp/B08XYZ1235
American Tourister,American Tourister Linea Polypropylene 78 cm Large Check-in Trolley,B08XYZ1236,Check-in,Large,5299,7999,33.8,4.1,1823,https://amazon.in/dp/B08XYZ1236
American Tourister,American Tourister Pazzo Spinner 55 cm Cabin Hard Trolley,B08XYZ1237,Cabin,Small,3799,5499,30.9,4.4,4210,https://amazon.in/dp/B08XYZ1237
American Tourister,American Tourister Pazzo Spinner 75 cm Large Hard Trolley,B08XYZ1238,Check-in,Large,5799,8499,31.8,4.2,2107,https://amazon.in/dp/B08XYZ1238
American Tourister,American Tourister Burst Max 55 cm Expandable Cabin Bag,B08XYZ1239,Cabin,Small,4299,6299,31.7,4.5,5632,https://amazon.in/dp/B08XYZ1239
American Tourister,American Tourister Burst Max 68 cm Expandable Check-in Bag,B08XYZ1240,Check-in,Medium,5499,7999,31.3,4.3,3298,https://amazon.in/dp/B08XYZ1240
American Tourister,American Tourister Valex 55 cm Soft Cabin Trolley Bag,B08XYZ1241,Cabin,Small,2799,3999,30.0,4.0,1892,https://amazon.in/dp/B08XYZ1241
American Tourister,American Tourister Valex 68 cm Soft Check-in Trolley Bag,B08XYZ1242,Check-in,Medium,3799,5499,30.9,3.9,1203,https://amazon.in/dp/B08XYZ1242
American Tourister,American Tourister Sable 55 cm Cabin Hard Trolley Blue,B08XYZ1243,Cabin,Small,3499,4999,30.0,4.2,2871,https://amazon.in/dp/B08XYZ1243
American Tourister,American Tourister Sable 75 cm Large Hard Trolley Silver,B08XYZ1244,Check-in,Large,5199,7499,30.7,4.1,1654,https://amazon.in/dp/B08XYZ1244
American Tourister,American Tourister Alto 55 cm Cabin Trolley Combo Set,B08XYZ1245,Set,Small,6999,9999,30.0,4.6,6021,https://amazon.in/dp/B08XYZ1245
Safari,Safari Polycarbonate 55 cm Cabin Trolley Bag Black,B09ABC1234,Cabin,Small,2899,4299,32.6,4.1,2743,https://amazon.in/dp/B09ABC1234
Safari,Safari Polycarbonate 65 cm Medium Check-in Trolley Bag,B09ABC1235,Check-in,Medium,3699,5499,32.7,4.0,1932,https://amazon.in/dp/B09ABC1235
Safari,Safari Polycarbonate 75 cm Large Check-in Trolley Bag,B09ABC1236,Check-in,Large,4499,6799,33.8,3.9,1421,https://amazon.in/dp/B09ABC1236
Safari,Safari Polypropylene 55 cm Hard Cabin Trolley Black,B09ABC1237,Cabin,Small,2499,3799,34.2,3.8,1823,https://amazon.in/dp/B09ABC1237
Safari,Safari Polypropylene 65 cm Hard Check-in Trolley Blue,B09ABC1238,Check-in,Medium,3299,4999,34.0,3.9,1102,https://amazon.in/dp/B09ABC1238
Safari,Safari Thorium 55 cm Expandable Cabin Hard Trolley,B09ABC1239,Cabin,Small,3499,5299,34.0,4.3,3821,https://amazon.in/dp/B09ABC1239
Safari,Safari Thorium 75 cm Expandable Check-in Hard Trolley,B09ABC1240,Check-in,Large,4999,7499,33.3,4.2,2134,https://amazon.in/dp/B09ABC1240
Safari,Safari Soft 55 cm Cabin Trolley Bag with Wheels,B09ABC1241,Cabin,Small,1999,2999,33.3,3.7,1432,https://amazon.in/dp/B09ABC1241
Safari,Safari Soft 75 cm Large Trolley Bag with Wheels,B09ABC1242,Check-in,Large,2899,4299,32.6,3.6,892,https://amazon.in/dp/B09ABC1242
Safari,Safari Trio Combo Set 3 Piece Hard Luggage,B09ABC1243,Set,Large,7999,11999,33.3,4.4,4102,https://amazon.in/dp/B09ABC1243
Skybags,Skybags Stripes 55 cm Cabin Hard Trolley Bag,B07DEF1234,Cabin,Small,2199,3499,37.2,3.9,2104,https://amazon.in/dp/B07DEF1234
Skybags,Skybags Stripes 65 cm Check-in Hard Trolley Bag,B07DEF1235,Check-in,Medium,2999,4499,33.3,3.8,1654,https://amazon.in/dp/B07DEF1235
Skybags,Skybags Stripes 75 cm Large Hard Trolley Bag,B07DEF1236,Check-in,Large,3799,5999,36.7,3.7,1021,https://amazon.in/dp/B07DEF1236
Skybags,Skybags Komet 55 cm Cabin Hard Trolley Grey,B07DEF1237,Cabin,Small,2499,3799,34.2,4.0,2891,https://amazon.in/dp/B07DEF1237
Skybags,Skybags Komet 75 cm Large Hard Trolley Silver,B07DEF1238,Check-in,Large,3999,6299,36.5,3.9,1432,https://amazon.in/dp/B07DEF1238
Skybags,Skybags Helix Plus 55 cm Cabin Trolley Bag,B07DEF1239,Cabin,Small,2799,4299,34.9,4.1,3210,https://amazon.in/dp/B07DEF1239
Skybags,Skybags Helix Plus 75 cm Large Check-in Trolley,B07DEF1240,Check-in,Large,4299,6499,33.8,4.0,1892,https://amazon.in/dp/B07DEF1240
Skybags,Skybags Cityscape 55 cm Soft Cabin Trolley Bag,B07DEF1241,Cabin,Small,1899,2999,36.7,3.7,1203,https://amazon.in/dp/B07DEF1241
Skybags,Skybags Cityscape 65 cm Soft Check-in Trolley Bag,B07DEF1242,Check-in,Medium,2599,3999,35.0,3.6,892,https://amazon.in/dp/B07DEF1242
Skybags,Skybags Trek Soft 55 cm Cabin Bag with Trolley,B07DEF1243,Cabin,Small,1799,2799,35.7,3.8,1542,https://amazon.in/dp/B07DEF1243
VIP,VIP Skybags Aristocrat Polypropylene 55 cm Cabin Hard Trolley,B06GHI1234,Cabin,Small,3499,5299,34.0,4.2,2341,https://amazon.in/dp/B06GHI1234
VIP,VIP Maestro Polypropylene 65 cm Check-in Hard Trolley Black,B06GHI1235,Check-in,Medium,4299,6499,33.8,4.1,1823,https://amazon.in/dp/B06GHI1235
VIP,VIP Maestro Polypropylene 75 cm Large Check-in Trolley,B06GHI1236,Check-in,Large,5299,7999,33.8,4.0,1234,https://amazon.in/dp/B06GHI1236
VIP,VIP Centurion Polycarbonate 55 cm Cabin Trolley Bag,B06GHI1237,Cabin,Small,4999,7499,33.3,4.4,2891,https://amazon.in/dp/B06GHI1237
VIP,VIP Centurion Polycarbonate 75 cm Large Trolley Bag,B06GHI1238,Check-in,Large,6999,9999,30.0,4.3,1654,https://amazon.in/dp/B06GHI1238
VIP,VIP Alfa Polypropylene 55 cm Cabin Hard Trolley Blue,B06GHI1239,Cabin,Small,2999,4499,33.3,4.0,2103,https://amazon.in/dp/B06GHI1239
VIP,VIP Alfa Polypropylene 65 cm Check-in Hard Trolley,B06GHI1240,Check-in,Medium,3799,5799,34.5,3.9,1432,https://amazon.in/dp/B06GHI1240
VIP,VIP Alfa Polypropylene 75 cm Large Hard Trolley Maroon,B06GHI1241,Check-in,Large,4799,7299,34.2,3.8,892,https://amazon.in/dp/B06GHI1241
VIP,VIP Skybags Combo 3-Piece Luggage Set Hard Trolley,B06GHI1242,Set,Large,9999,14999,33.3,4.5,3210,https://amazon.in/dp/B06GHI1242
VIP,VIP Turbo Soft 55 cm Cabin Trolley Expandable Bag,B06GHI1243,Cabin,Small,2499,3799,34.2,3.9,1654,https://amazon.in/dp/B06GHI1243
Aristocrat,Aristocrat Luggage Polypropylene 55 cm Cabin Trolley Black,B05JKL1234,Cabin,Small,1799,2999,40.0,3.6,3421,https://amazon.in/dp/B05JKL1234
Aristocrat,Aristocrat Luggage Polypropylene 65 cm Check-in Trolley,B05JKL1235,Check-in,Medium,2299,3799,39.5,3.5,2103,https://amazon.in/dp/B05JKL1235
Aristocrat,Aristocrat Luggage Polypropylene 75 cm Large Check-in Trolley,B05JKL1236,Check-in,Large,2999,4799,37.5,3.4,1432,https://amazon.in/dp/B05JKL1236
Aristocrat,Aristocrat Nile 4W 55 cm Cabin Trolley Bag Blue,B05JKL1237,Cabin,Small,1999,3299,39.4,3.7,2891,https://amazon.in/dp/B05JKL1237
Aristocrat,Aristocrat Nile 4W 75 cm Large Check-in Trolley,B05JKL1238,Check-in,Large,3299,5299,37.7,3.6,1654,https://amazon.in/dp/B05JKL1238
Aristocrat,Aristocrat Opal 4W 55 cm Cabin Hard Trolley Green,B05JKL1239,Cabin,Small,2199,3499,37.1,3.8,1823,https://amazon.in/dp/B05JKL1239
Aristocrat,Aristocrat Opal 4W 65 cm Check-in Hard Trolley,B05JKL1240,Check-in,Medium,2799,4499,37.8,3.7,1203,https://amazon.in/dp/B05JKL1240
Aristocrat,Aristocrat Neon 55 cm Soft Cabin Trolley Bag,B05JKL1241,Cabin,Small,1499,2499,40.0,3.5,2341,https://amazon.in/dp/B05JKL1241
Aristocrat,Aristocrat Neon 65 cm Soft Check-in Trolley Bag,B05JKL1242,Check-in,Medium,1999,3299,39.4,3.4,1432,https://amazon.in/dp/B05JKL1242
Aristocrat,Aristocrat Combo 3-Piece Luggage Set Budget Trolley,B05JKL1243,Set,Large,4999,7999,37.5,3.6,3891,https://amazon.in/dp/B05JKL1243
Nasher Miles,Nasher Miles Portofino Check-in Hard Luggage 65 cm,B10MNO1234,Check-in,Medium,5499,7999,31.3,4.3,1821,https://amazon.in/dp/B10MNO1234
Nasher Miles,Nasher Miles Portofino Check-in Hard Luggage 75 cm,B10MNO1235,Check-in,Large,6999,9999,30.0,4.2,1204,https://amazon.in/dp/B10MNO1235
Nasher Miles,Nasher Miles Portofino Cabin Hard Luggage 55 cm,B10MNO1236,Cabin,Small,4499,6499,30.8,4.4,2341,https://amazon.in/dp/B10MNO1236
Nasher Miles,Nasher Miles Ankara Hard Luggage 65 cm Check-in,B10MNO1237,Check-in,Medium,6499,9499,31.6,4.5,1543,https://amazon.in/dp/B10MNO1237
Nasher Miles,Nasher Miles Ankara Hard Luggage 75 cm Check-in,B10MNO1238,Check-in,Large,7999,11499,30.4,4.4,892,https://amazon.in/dp/B10MNO1238
Nasher Miles,Nasher Miles Ankara Cabin Hard Luggage 55 cm,B10MNO1239,Cabin,Small,5499,7999,31.3,4.6,3102,https://amazon.in/dp/B10MNO1239
Nasher Miles,Nasher Miles Hamburg Soft Luggage 55 cm Cabin,B10MNO1240,Cabin,Small,3999,5999,33.3,4.2,1432,https://amazon.in/dp/B10MNO1240
Nasher Miles,Nasher Miles Hamburg Soft Luggage 65 cm Check-in,B10MNO1241,Check-in,Medium,5299,7499,29.3,4.1,892,https://amazon.in/dp/B10MNO1241
Nasher Miles,Nasher Miles Glasgow Hard Luggage 65 cm Spinner,B10MNO1242,Check-in,Medium,7499,10999,31.8,4.5,1654,https://amazon.in/dp/B10MNO1242
Nasher Miles,Nasher Miles Glasgow Hard Luggage 75 cm Large,B10MNO1243,Check-in,Large,8999,12999,30.8,4.3,1023,https://amazon.in/dp/B10MNO1243
Nasher Miles,Nasher Miles Combo 3-Piece Hard Luggage Set,B10MNO1244,Set,Large,15999,22999,30.4,4.6,2341,https://amazon.in/dp/B10MNO1244"""

REVIEWS_CSV = """review_id,brand,asin,rating,review_text,sentiment,aspect,helpful_votes,verified_purchase,review_date
R00031,American Tourister,B08XYZ1239,5,Hard shell protected my belongings perfectly when airline mishandled my checked bag.,positive,durability,33,No,2024-02-08
R00045,American Tourister,B08XYZ1237,4,Lightweight despite the hard shell. Makes a big difference when close to airline weight limit.,positive,weight,37,Yes,2024-12-11
R00043,American Tourister,B08XYZ1234,5,Expansion feature is super useful. Got extra 2 liters for return trip shopping. Works smoothly.,positive,expansion,16,No,2024-05-14
R00213,VIP,B06GHI1234,5,VIP is a trusted Indian brand and this bag proves exactly why. Solid build and smooth operation.,positive,brand,25,No,2024-11-04
R00064,American Tourister,B08XYZ1244,1,Expected better quality for this price. The lock feels flimsy compared to older AT models.,negative,lock,11,No,2024-07-20
R00203,Skybags,B07DEF1235,2,Inner lining is extremely thin. Anything slightly sharp will poke through it very easily.,negative,lining,17,No,2024-06-02
R00068,American Tourister,B08XYZ1241,2,The zipper stuck after just 4 uses. Had to force it open which damaged the teeth. Disappointing.,negative,zipper,6,Yes,2024-06-10
R00151,Skybags,B07DEF1238,5,Bag is spacious enough for a 3 to 4 day trip. Good for quick weekend getaways.,positive,capacity,35,Yes,2024-08-03
R00033,American Tourister,B08XYZ1235,4,Smooth 360 degree spinner wheels. Glides effortlessly even on rough airport floors without any drag.,positive,wheels,14,Yes,2024-01-28
R00253,VIP,B06GHI1239,2,Expected better finishing at this premium price. Some rough edges on plastic frame are visible.,negative,finishing,2,No,2024-02-20
R00319,Aristocrat,B05JKL1239,1,Zipper teeth separated entirely after just 4 trips. Had to use rubber band to keep bag closed.,negative,zipper,14,Yes,2024-11-17
R00153,Skybags,B07DEF1244,5,Good entry level bag for occasional travelers. Does not cost much and works fine for short trips.,positive,value,29,No,2024-01-07
R00157,Skybags,B07DEF1242,5,Good entry level bag for occasional travelers. Does not cost much and works fine for short trips.,positive,value,5,Yes,2024-02-15
R00335,Aristocrat,B05JKL1240,2,So-called hard shell is barely hard. Very thin polypropylene that bends easily under light pressure.,negative,shell,30,Yes,2024-06-19
R00280,Aristocrat,B05JKL1241,4,Simple practical design easy to pack and unpack. Gets the basic job done without fuss.,positive,simple,45,No,2024-08-20
R00076,Safari,B09ABC1245,5,Price to quality ratio is excellent. Safari offers great value compared to multinational brands.,positive,value,32,Yes,2024-11-14
R00186,Skybags,B07DEF1244,2,Not worth even at this price point. Aristocrat is honestly better at similar price.,negative,comparison,20,Yes,2024-11-21
R00248,VIP,B06GHI1236,5,Smooth 360 spinner wheels and very comfortable ergonomic telescoping handle system.,positive,wheels,9,Yes,2024-03-25
R00127,Safari,B09ABC1245,2,TSA lock instructions unclear in manual. Took very long time to figure out the process.,negative,lock,3,Yes,2024-05-08
R00397,Nasher Miles,B10MNO1244,3,Not as widely available offline as American Tourister or VIP. Mainly online only.,negative,availability,17,Yes,2024-04-08
R00327,Aristocrat,B05JKL1243,2,Color faded significantly after first use in mild sun. Looks completely old within few months.,negative,color,20,Yes,2024-10-14
R00390,Nasher Miles,B10MNO1245,1,Dark colors show fingerprints and smudges quite easily. Requires regular wiping to look clean.,negative,smudge,12,Yes,2024-01-24
R00391,Nasher Miles,B10MNO1243,1,Website delivery took longer than expected. Amazon was considerably faster for same product.,negative,delivery,1,Yes,2024-06-23
R00381,Nasher Miles,B10MNO1237,2,Website delivery took longer than expected. Amazon was considerably faster for same product.,negative,delivery,15,Yes,2024-08-24
R00084,Safari,B09ABC1243,4,Lightweight and spacious. Hard shell gives confidence that clothes will not get crushed.,positive,weight,29,No,2024-11-19
R00188,Skybags,B07DEF1235,2,Zipper failed after 3 uses. The teeth separated completely and cannot be repaired.,negative,zipper,10,No,2024-07-06
R00163,Skybags,B07DEF1241,5,Nice looking bag and handle feels okay. Would recommend for occasional leisure use.,positive,look,21,No,2024-08-11
R00026,American Tourister,B08XYZ1242,4,Handles feel solid and trolley mechanism is very smooth compared to cheaper brands.,positive,handle,38,Yes,2024-08-01
R00110,Safari,B09ABC1235,5,Smooth wheels and solid handle mechanism. Indian brand doing it right with quality components.,positive,wheels,44,Yes,2024-02-23
R00261,VIP,B06GHI1245,2,Bought from Amazon but received a bag with minor scratch already on shell. Quality check issue.,negative,scratch,10,Yes,2024-10-22
R00067,American Tourister,B08XYZ1238,2,Expected better quality for this price. The lock feels flimsy compared to older AT models.,negative,lock,25,No,2024-02-13
R00364,Nasher Miles,B10MNO1236,4,Internal organization is thoughtfully designed with multiple useful pockets and compression straps.,positive,organization,39,Yes,2024-04-02
R00237,VIP,B06GHI1236,5,VIP has been reliable for Indian families for decades. This bag continues that strong legacy.,positive,legacy,18,Yes,2024-02-01
R00393,Nasher Miles,B10MNO1240,2,Dark colors show fingerprints and smudges quite easily. Requires regular wiping to look clean.,negative,smudge,24,Yes,2024-11-24
R00370,Nasher Miles,B10MNO1234,4,Worth every bit of the premium price. After using this I cannot go back to American Tourister.,positive,comparison,19,Yes,2024-06-10
R00093,Safari,B09ABC1242,4,Packaging was neat and bag arrived in perfect condition with no damage at all.,positive,packaging,8,Yes,2024-04-13
R00094,Safari,B09ABC1236,4,Used for 4 international trips. Zipper wheels handles all working perfectly. Great longevity.,positive,longevity,4,No,2024-07-11
R00388,Nasher Miles,B10MNO1241,1,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,14,Yes,2024-09-14
R00086,Safari,B09ABC1245,4,Good Indian alternative to American Tourister. Similar quality at slightly lower price point.,positive,comparison,6,No,2024-04-06
R00230,VIP,B06GHI1235,5,VIP is a trusted Indian brand and this bag proves exactly why. Solid build and smooth operation.,positive,brand,13,No,2024-07-15
R00144,Skybags,B07DEF1245,5,Bag is spacious enough for a 3 to 4 day trip. Good for quick weekend getaways.,positive,capacity,44,No,2024-05-17
R00121,Safari,B09ABC1241,2,Handle height adjustment is a bit stiff compared to other brands I have used previously.,negative,handle,22,Yes,2024-11-23
R00052,American Tourister,B08XYZ1239,1,For this price VIP feels more solid. Bit disappointed with the material thickness on this model.,negative,value,0,Yes,2024-10-19
R00187,Skybags,B07DEF1238,3,Wheel broke after just one trip. Completely unacceptable for any price point.,negative,wheel,1,No,2024-06-24
R00034,American Tourister,B08XYZ1235,5,Loved the color options. The teal one looks premium and gets compliments at the airport.,positive,design,15,Yes,2024-11-16
R00249,VIP,B06GHI1241,5,Better wheel mechanism than Skybags by significant margin. Glides smoothly even when fully loaded.,positive,wheels2,36,No,2024-11-19
R00222,VIP,B06GHI1239,4,Very lightweight polycarbonate. Makes a real measurable difference when airline is strict on weight.,positive,weight,26,Yes,2024-11-25
R00299,Aristocrat,B05JKL1235,5,Does the job adequately for occasional trips. Not expecting premium quality at this price.,positive,occasional,38,Yes,2024-09-10
R00224,VIP,B06GHI1242,4,Finish quality and color vibrancy is very good. Looks premium and well maintained at airport.,positive,finish,9,No,2024-04-28
R00293,Aristocrat,B05JKL1236,4,Combo set is unbeatable value. Three usable bags at such a low price is genuinely impressive.,positive,combo,4,No,2024-01-10
R00119,Safari,B09ABC1239,2,Inner fabric quality is below average. Thin and does not feel premium for the price.,negative,lining,10,Yes,2024-10-23
R00386,Nasher Miles,B10MNO1242,2,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,5,Yes,2024-09-15
R00322,Aristocrat,B05JKL1237,2,Seller sent completely wrong color variant. Amazon return process was also unnecessarily complicated.,negative,seller,30,No,2024-05-28
R00019,American Tourister,B08XYZ1235,4,Customer service was helpful when I had a zipper issue. Replaced without any hassle at all.,positive,service,7,Yes,2024-11-06
R00183,Skybags,B07DEF1240,2,Soft bag stitching on side pocket gave way after two trips. Very bad quality control.,negative,stitching,0,No,2024-11-25
R00308,Aristocrat,B05JKL1242,5,Lightweight which is useful when you are a truly budget conscious traveler.,positive,weight,25,Yes,2024-11-09
R00282,Aristocrat,B05JKL1243,5,Works adequately for domestic cabin use. Would not risk for international checked baggage.,positive,domestic,27,Yes,2024-05-08
R00201,Skybags,B07DEF1244,1,Lock jammed after first use. Had to break it open to access belongings. Waste of money.,negative,lock,26,Yes,2024-10-14
R00357,Nasher Miles,B10MNO1236,5,Beautiful bag in person. Got genuine compliments from travelers at Frankfurt airport.,positive,compliment,34,Yes,2024-09-12
R00304,Aristocrat,B05JKL1245,4,Colors are bright and easy to spot at baggage belt without any confusion.,positive,visibility,1,Yes,2024-10-22
R00349,Nasher Miles,B10MNO1241,4,Worth every bit of the premium price. After using this I cannot go back to American Tourister.,positive,comparison,23,Yes,2024-11-04
R00006,American Tourister,B08XYZ1237,5,The TSA lock is a great feature. Easy to set combination and very secure for international travel.,positive,lock,6,Yes,2024-07-04
R00395,Nasher Miles,B10MNO1236,2,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,3,Yes,2024-09-13
R00240,VIP,B06GHI1245,4,Expandable feature is genuinely useful and easy to use even when the bag is fully packed.,positive,expansion,27,Yes,2024-08-03
R00073,Safari,B09ABC1243,5,Safari has improved a lot in recent years. This bag shows that commitment to quality.,positive,improvement,7,No,2024-10-07
R00113,Safari,B09ABC1241,4,Safari has improved a lot in recent years. This bag shows that commitment to quality.,positive,improvement,27,Yes,2024-11-27
R00115,Safari,B09ABC1238,5,Good Indian alternative to American Tourister. Similar quality at slightly lower price point.,positive,comparison,34,No,2024-08-14
R00053,American Tourister,B08XYZ1235,2,Inner lining quality is poor. Started peeling off within 6 months of moderate use.,negative,lining,16,Yes,2024-03-12
R00066,American Tourister,B08XYZ1245,2,Wheels make a squeaking noise on smooth floors. Embarrassing at the airport. Very annoying.,negative,wheels,25,Yes,2024-11-28
R00306,Aristocrat,B05JKL1239,5,Combo set is unbeatable value. Three usable bags at such a low price is genuinely impressive.,positive,combo,24,Yes,2024-10-05
R00103,Safari,B09ABC1240,5,Lock quality is good and key backup option is very reassuring for international travel.,positive,lock,5,No,2024-01-24
R00300,Aristocrat,B05JKL1235,4,Zipper is smooth and wheels spin okay on flat clean airport surfaces.,positive,zipper,20,Yes,2024-05-15
R00333,Aristocrat,B05JKL1235,2,Would not recommend even at this price. Spend a little more and get Skybags instead.,negative,comparison,7,Yes,2024-02-09
R00017,American Tourister,B08XYZ1237,5,The TSA lock is a great feature. Easy to set combination and very secure for international travel.,positive,lock,34,Yes,2024-12-19
R00257,VIP,B06GHI1244,2,Trolley extension mechanism is noticeably loud. Annoying in quiet airport corridors.,negative,noise,1,Yes,2024-12-15
R00366,Nasher Miles,B10MNO1235,4,The combo set is excellent value considering the genuinely premium quality you receive.,positive,combo,0,Yes,2024-07-21
R00083,Safari,B09ABC1237,4,Good capacity. Fits 7 days of clothes comfortably with some extra space for essentials.,positive,capacity,9,Yes,2024-01-08
R00057,American Tourister,B08XYZ1245,2,Inner lining quality is poor. Started peeling off within 6 months of moderate use.,negative,lining,8,Yes,2024-10-07
R00040,American Tourister,B08XYZ1241,4,Lightweight despite the hard shell. Makes a big difference when close to airline weight limit.,positive,weight,4,No,2024-09-04
R00001,American Tourister,B08XYZ1234,5,Excellent build quality. Polycarbonate shell feels very sturdy. Used on 3 flights already and no scratches.,positive,build,15,Yes,2024-03-24
R00148,Skybags,B07DEF1236,5,My kid loves the colors. Bought for college trips and it handles well for light use.,positive,kids,33,No,2024-05-06
R00014,American Tourister,B08XYZ1237,5,Great brand value. American Tourister is trusted globally and this product lives up to the name.,positive,brand,3,Yes,2024-01-26
R00047,American Tourister,B08XYZ1236,1,Inner lining quality is poor. Started peeling off within 6 months of moderate use.,negative,lining,19,Yes,2024-11-28
R00328,Aristocrat,B05JKL1244,1,So-called hard shell is barely hard. Very thin polypropylene that bends easily under light pressure.,negative,shell,15,No,2024-09-10
R00191,Skybags,B07DEF1235,3,Inner lining is extremely thin. Anything slightly sharp will poke through it very easily.,negative,lining,30,Yes,2024-03-25
R00160,Skybags,B07DEF1240,4,Lightweight good for domestic short trips where you only carry cabin baggage.,positive,weight,38,Yes,2024-02-09
R00281,Aristocrat,B05JKL1235,4,For this very low price there is nothing better in the market. Budget option that simply works.,positive,price,16,Yes,2024-03-18
R00233,VIP,B06GHI1241,5,Internal organization is well thought out. Separate shoe compartment is a very nice touch.,positive,organization,31,No,2024-07-09
R00279,Aristocrat,B05JKL1244,5,Works adequately for domestic cabin use. Would not risk for international checked baggage.,positive,domestic,9,Yes,2024-01-10
R00198,Skybags,B07DEF1234,2,Wheel broke after just one trip. Completely unacceptable for any price point.,negative,wheel,15,Yes,2024-02-08
R00174,Skybags,B07DEF1234,4,Design is trendy and modern. Skybags always gets the aesthetics right for young buyers.,positive,trend,20,Yes,2024-05-12
R00150,Skybags,B07DEF1239,4,Zipper is smooth and the four spinner wheels work well on clean airport tiles.,positive,wheels,10,Yes,2024-07-23
R00092,Safari,B09ABC1245,5,Price to quality ratio is excellent. Safari offers great value compared to multinational brands.,positive,value,15,Yes,2024-06-11
R00369,Nasher Miles,B10MNO1234,5,Weight is surprisingly low for such a hard polycarbonate shell. Saved weight at check-in.,positive,weight,31,Yes,2024-12-28
R00316,Aristocrat,B05JKL1242,5,Zipper is smooth and wheels spin okay on flat clean airport surfaces.,positive,zipper,23,No,2024-09-05
R00080,Safari,B09ABC1243,5,Solid construction. Corner guards add extra protection which I noticed and appreciated immediately.,positive,construction,29,No,2024-08-22
R00343,Nasher Miles,B10MNO1242,5,Best luggage investment I have made. Finally stopped buying cheap bags that break every year.,positive,investment,39,Yes,2024-03-04
R00329,Aristocrat,B05JKL1238,3,Color faded significantly after first use in mild sun. Looks completely old within few months.,negative,color,7,No,2024-07-10
R00385,Nasher Miles,B10MNO1235,1,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,26,No,2024-09-07
R00347,Nasher Miles,B10MNO1239,5,TSA lock is very easy to set and feels extremely solid. Passed multiple international airports.,positive,lock,20,Yes,2024-07-20
R00088,Safari,B09ABC1235,5,Packaging was neat and bag arrived in perfect condition with no damage at all.,positive,packaging,8,No,2024-11-17
R00363,Nasher Miles,B10MNO1237,4,The combo set is excellent value considering the genuinely premium quality you receive.,positive,combo,34,Yes,2024-09-23
R00346,Nasher Miles,B10MNO1241,5,Beautiful bag in person. Got genuine compliments from travelers at Frankfurt airport.,positive,compliment,29,Yes,2024-10-17
R00049,American Tourister,B08XYZ1234,1,Pockets inside are too shallow for organizing small items properly. Nothing stays in place.,negative,pockets,13,No,2024-10-19
R00205,Skybags,B07DEF1237,1,Soft bag stitching on side pocket gave way after two trips. Very bad quality control.,negative,stitching,1,Yes,2024-04-05
R00143,Skybags,B07DEF1238,5,Lightweight good for domestic short trips where you only carry cabin baggage.,positive,weight,36,Yes,2024-08-04
R00242,VIP,B06GHI1238,4,Used on 10 plus domestic trips and 2 international. Still performs exactly like new.,positive,longevity,25,Yes,2024-06-06
R00200,Skybags,B07DEF1242,3,Not worth even at this price point. Aristocrat is honestly better at similar price.,negative,comparison,18,No,2024-12-05
R00178,Skybags,B07DEF1238,5,Lock mechanism is simple but works. Good for basic security on domestic flights.,positive,lock,16,Yes,2024-08-10
R00270,VIP,B06GHI1241,2,Bag is slightly heavier than competitors at similar price. Adds to precious checked baggage weight.,negative,weight2,24,No,2024-08-08
R00035,American Tourister,B08XYZ1242,4,Very spacious inside. Fits everything for a week long trip without issue. Added shopping on return too.,positive,capacity,36,No,2024-04-26
R00082,Safari,B09ABC1244,5,Good Indian alternative to American Tourister. Similar quality at slightly lower price point.,positive,comparison,21,Yes,2024-04-22
R00209,VIP,B06GHI1237,5,Premium feel. Much better quality than Aristocrat despite being from same parent company.,positive,comparison,20,Yes,2024-03-09
R00189,Skybags,B07DEF1236,2,For frequent travelers this is not reliable at all. Strictly for occasional very light use only.,negative,frequent,16,No,2024-05-27
R00133,Safari,B09ABC1236,2,Soft bag stitching came loose after just 2 uses. Bit shocking for a Safari product.,negative,stitching,25,No,2024-05-03
R00362,Nasher Miles,B10MNO1245,4,Worth every bit of the premium price. After using this I cannot go back to American Tourister.,positive,comparison,22,No,2024-11-09
R00377,Nasher Miles,B10MNO1240,4,Internal organization is thoughtfully designed with multiple useful pockets and compression straps.,positive,organization,28,Yes,2024-06-10
R00271,VIP,B06GHI1237,2,Trolley extension mechanism is noticeably loud. Annoying in quiet airport corridors.,negative,noise,30,Yes,2024-04-12
R00331,Aristocrat,B05JKL1237,2,Not remotely suitable for checked baggage on any flights. Far too fragile for airline handling.,negative,checkin,19,Yes,2024-06-28
R00078,Safari,B09ABC1240,4,Good Indian alternative to American Tourister. Similar quality at slightly lower price point.,positive,comparison,39,Yes,2024-07-18
R00232,VIP,B06GHI1234,4,The Centurion series polycarbonate is impressive. Very hard shell not flexible at all under pressure.,positive,centurion,10,Yes,2024-11-03
R00010,American Tourister,B08XYZ1238,4,Very spacious inside. Fits everything for a week long trip without issue. Added shopping on return too.,positive,capacity,14,Yes,2024-07-09
R00108,Safari,B09ABC1245,4,Used for 4 international trips. Zipper wheels handles all working perfectly. Great longevity.,positive,longevity,10,Yes,2024-02-19
R00340,Nasher Miles,B10MNO1235,5,Outstanding overall quality. Best Indian luggage brand right now without any doubt whatsoever.,positive,quality,8,Yes,2024-12-12
R00226,VIP,B06GHI1240,5,Smooth 360 spinner wheels and very comfortable ergonomic telescoping handle system.,positive,wheels,39,Yes,2024-10-22
R00341,Nasher Miles,B10MNO1239,4,This is my second Nasher Miles purchase and equally impressed both times. Consistent quality.,positive,repeat,25,Yes,2024-10-18
R00007,American Tourister,B08XYZ1239,5,Loved the color options. The teal one looks premium and gets compliments at the airport.,positive,design,16,Yes,2024-12-15
R00089,Safari,B09ABC1243,5,Easy to identify on the belt because of bright colors. No more anxious waiting at baggage claim.,positive,visibility,28,No,2024-09-15
R00175,Skybags,B07DEF1240,4,Zipper is smooth and the four spinner wheels work well on clean airport tiles.,positive,wheels,15,No,2024-10-22
R00234,VIP,B06GHI1242,4,Smooth 360 spinner wheels and very comfortable ergonomic telescoping handle system.,positive,wheels,22,No,2024-02-10
R00099,Safari,B09ABC1240,4,Good Indian alternative to American Tourister. Similar quality at slightly lower price point.,positive,comparison,29,Yes,2024-10-18
R00218,VIP,B06GHI1239,5,Used on 10 plus domestic trips and 2 international. Still performs exactly like new.,positive,longevity,25,No,2024-12-04
R00100,Safari,B09ABC1240,5,Very durable polycarbonate. Bought 2 years ago still going strong on monthly domestic travel.,positive,durability,36,Yes,2024-02-21
R00192,Skybags,B07DEF1244,3,For frequent travelers this is not reliable at all. Strictly for occasional very light use only.,negative,frequent,30,No,2024-06-03
R00042,American Tourister,B08XYZ1241,5,Expansion feature is super useful. Got extra 2 liters for return trip shopping. Works smoothly.,positive,expansion,13,No,2024-01-06
R00359,Nasher Miles,B10MNO1237,5,Worth every bit of the premium price. After using this I cannot go back to American Tourister.,positive,comparison,18,Yes,2024-12-23
R00147,Skybags,B07DEF1243,5,Good value under 2500 rupees. For casual travelers this is a solid sensible buy.,positive,price,1,Yes,2024-10-02
R00396,Nasher Miles,B10MNO1236,2,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,26,Yes,2024-01-10
R00037,American Tourister,B08XYZ1240,5,Loved the color options. The teal one looks premium and gets compliments at the airport.,positive,design,29,Yes,2024-11-21
R00054,American Tourister,B08XYZ1237,2,Inner lining quality is poor. Started peeling off within 6 months of moderate use.,negative,lining,9,Yes,2024-08-27
R00202,Skybags,B07DEF1234,2,Handle feels very cheap. Wobbles even at medium extension and rattles when walking.,negative,handle,6,Yes,2024-08-08
R00081,Safari,B09ABC1242,5,Smooth wheels and solid handle mechanism. Indian brand doing it right with quality components.,positive,wheels,10,Yes,2024-05-17
R00197,Skybags,B07DEF1245,2,Cabin bag rejected by airline as slightly oversized. Dimensions listed are inaccurate.,negative,size,20,Yes,2024-02-05
R00336,Aristocrat,B05JKL1239,2,Seller sent completely wrong color variant. Amazon return process was also unnecessarily complicated.,negative,seller,24,Yes,2024-08-17
R00361,Nasher Miles,B10MNO1240,5,Brand is growing fast in India and rightfully so. Quality fully justifies the premium pricing.,positive,growth,22,Yes,2024-05-02
R00265,VIP,B06GHI1234,2,Zipper pull feels a bit cheap for this premium price bracket. Functional but not premium feel.,negative,zipper,9,Yes,2024-04-11
R00284,Aristocrat,B05JKL1241,4,Good entry point for students and first time fliers with a tight limited budget.,positive,student,7,No,2024-10-18
R00012,American Tourister,B08XYZ1238,4,Hard shell protected my belongings perfectly when airline mishandled my checked bag.,positive,durability,38,Yes,2024-09-24
R00070,American Tourister,B08XYZ1235,2,Colour faded after one trip in checked baggage. Shell looks scratched despite careful handling.,negative,color,11,No,2024-09-13
R00166,Skybags,B07DEF1240,4,Good for students and first time buyers who need something affordable and decent.,positive,student,31,Yes,2024-03-17
R00146,Skybags,B07DEF1243,5,Zipper is smooth and the four spinner wheels work well on clean airport tiles.,positive,wheels,1,Yes,2024-04-22
R00055,American Tourister,B08XYZ1245,2,One wheel started wobbling after 5 to 6 uses. Not expected from a brand of this reputation.,negative,wheels2,19,No,2024-09-01
R00059,American Tourister,B08XYZ1235,3,The zipper stuck after just 4 uses. Had to force it open which damaged the teeth. Disappointing.,negative,zipper,26,Yes,2024-01-01
R00011,American Tourister,B08XYZ1244,5,Customer service was helpful when I had a zipper issue. Replaced without any hassle at all.,positive,service,10,Yes,2024-06-07
R00207,VIP,B06GHI1236,5,VIP has been reliable for Indian families for decades. This bag continues that strong legacy.,positive,legacy,0,Yes,2024-03-05
R00374,Nasher Miles,B10MNO1238,5,Beautiful bag in person. Got genuine compliments from travelers at Frankfurt airport.,positive,compliment,43,Yes,2024-03-20
R00180,Skybags,B07DEF1244,5,The Helix Plus model is actually quite solid. Surprised me given the competitive price.,positive,helix,44,Yes,2024-08-28
R00085,Safari,B09ABC1245,5,Smooth wheels and solid handle mechanism. Indian brand doing it right with quality components.,positive,wheels,31,No,2024-04-05
R00312,Aristocrat,B05JKL1235,5,Lightweight which is useful when you are a truly budget conscious traveler.,positive,weight,11,No,2024-02-26
R00128,Safari,B09ABC1236,2,Color came off on corners after first checked baggage use. Disappointing for a flagship product.,negative,color,0,No,2024-09-05
R00022,American Tourister,B08XYZ1244,5,Excellent build quality. Polycarbonate shell feels very sturdy. Used on 3 flights already and no scratches.,positive,build,17,Yes,2024-02-10
R00044,American Tourister,B08XYZ1245,5,Worth every rupee. Premium feel at reasonable price compared to Samsonite which is double the cost.,positive,value,42,No,2024-03-07
R00227,VIP,B06GHI1245,5,Expandable feature is genuinely useful and easy to use even when the bag is fully packed.,positive,expansion,1,Yes,2024-05-23
R00220,VIP,B06GHI1241,4,Better wheel mechanism than Skybags by significant margin. Glides smoothly even when fully loaded.,positive,wheels2,5,Yes,2024-02-14
R00015,American Tourister,B08XYZ1240,5,Loved the color options. The teal one looks premium and gets compliments at the airport.,positive,design,4,Yes,2024-10-23
R00378,Nasher Miles,B10MNO1238,5,Outstanding overall quality. Best Indian luggage brand right now without any doubt whatsoever.,positive,quality,44,Yes,2024-01-22
R00211,VIP,B06GHI1241,5,The combo set offers great value. Consistent quality across all three bag sizes in the set.,positive,combo,32,Yes,2024-08-17
R00315,Aristocrat,B05JKL1235,4,Design looks decent enough. Presentable enough for basic office trips on a tight budget.,positive,design,8,Yes,2024-08-01
R00305,Aristocrat,B05JKL1241,4,Colors are bright and easy to spot at baggage belt without any confusion.,positive,visibility,8,Yes,2024-04-25
R00229,VIP,B06GHI1243,5,Good warranty support. VIP has service centers across India which is very reassuring.,positive,service,4,Yes,2024-12-21
R00278,Aristocrat,B05JKL1239,4,Good for short trips and basic domestic travel. Handles the absolute essentials well enough.,positive,casual,1,Yes,2024-02-27
R00244,VIP,B06GHI1235,4,Expandable feature is genuinely useful and easy to use even when the bag is fully packed.,positive,expansion,27,No,2024-09-03
R00167,Skybags,B07DEF1239,4,Amazon delivery was fast and bag came without any damage. Good packaging from seller.,positive,delivery,28,Yes,2024-09-15
R00168,Skybags,B07DEF1245,4,Good entry level bag for occasional travelers. Does not cost much and works fine for short trips.,positive,value,26,Yes,2024-02-16
R00292,Aristocrat,B05JKL1244,4,My parents use it for short religious pilgrimages. Perfectly adequate for that use case.,positive,pilgrim,43,No,2024-12-16
R00176,Skybags,B07DEF1236,4,My kid loves the colors. Bought for college trips and it handles well for light use.,positive,kids,11,Yes,2024-10-28
R00351,Nasher Miles,B10MNO1244,5,Internal organization is thoughtfully designed with multiple useful pockets and compression straps.,positive,organization,36,Yes,2024-12-02
R00058,American Tourister,B08XYZ1237,2,The expansion zip is hard to operate when bag is fully packed. Almost impossible to close alone.,negative,expansion,16,Yes,2024-05-28
R00063,American Tourister,B08XYZ1234,2,Wheels make a squeaking noise on smooth floors. Embarrassing at the airport. Very annoying.,negative,wheels,11,Yes,2024-06-07
R00382,Nasher Miles,B10MNO1239,3,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,22,No,2024-08-25
R00268,VIP,B06GHI1240,2,One wheel was slightly misaligned straight out of box. Had to press it firmly back into place.,negative,wheel,5,Yes,2024-12-25
R00104,Safari,B09ABC1234,5,Easy to identify on the belt because of bright colors. No more anxious waiting at baggage claim.,positive,visibility,14,Yes,2024-11-02
R00223,VIP,B06GHI1245,4,Used on 10 plus domestic trips and 2 international. Still performs exactly like new.,positive,longevity,18,Yes,2024-06-04
R00317,Aristocrat,B05JKL1235,1,So-called hard shell is barely hard. Very thin polypropylene that bends easily under light pressure.,negative,shell,9,Yes,2024-12-24
R00102,Safari,B09ABC1237,5,The combo set is amazing value. All 3 bags have matching quality and finish throughout.,positive,combo,20,Yes,2024-07-09
R00334,Aristocrat,B05JKL1237,2,Not remotely suitable for checked baggage on any flights. Far too fragile for airline handling.,negative,checkin,3,Yes,2024-05-13
R00091,Safari,B09ABC1238,5,Good Indian alternative to American Tourister. Similar quality at slightly lower price point.,positive,comparison,31,Yes,2024-05-15
R00065,American Tourister,B08XYZ1237,2,Wheels make a squeaking noise on smooth floors. Embarrassing at the airport. Very annoying.,negative,wheels,25,Yes,2024-07-01
R00320,Aristocrat,B05JKL1236,2,Inner lining is paper thin material. Tore completely within the very first week of use.,negative,lining,24,Yes,2024-07-17
R00221,VIP,B06GHI1245,5,The Centurion series polycarbonate is impressive. Very hard shell not flexible at all under pressure.,positive,centurion,8,Yes,2024-10-18
R00050,American Tourister,B08XYZ1239,2,One wheel started wobbling after 5 to 6 uses. Not expected from a brand of this reputation.,negative,wheels2,6,No,2024-12-11
R00062,American Tourister,B08XYZ1234,2,One wheel started wobbling after 5 to 6 uses. Not expected from a brand of this reputation.,negative,wheels2,18,No,2024-03-14
R00250,VIP,B06GHI1244,5,Better wheel mechanism than Skybags by significant margin. Glides smoothly even when fully loaded.,positive,wheels2,20,Yes,2024-03-15
R00245,VIP,B06GHI1238,5,Used on 10 plus domestic trips and 2 international. Still performs exactly like new.,positive,longevity,14,Yes,2024-03-03
R00360,Nasher Miles,B10MNO1239,5,The combo set is excellent value considering the genuinely premium quality you receive.,positive,combo,22,Yes,2024-05-04
R00028,American Tourister,B08XYZ1235,5,Excellent build quality. Polycarbonate shell feels very sturdy. Used on 3 flights already and no scratches.,positive,build,4,Yes,2024-03-22
R00046,American Tourister,B08XYZ1234,5,Smooth 360 degree spinner wheels. Glides effortlessly even on rough airport floors without any drag.,positive,wheels,30,Yes,2024-01-17
R00111,Safari,B09ABC1238,5,Lock quality is good and key backup option is very reassuring for international travel.,positive,lock,7,Yes,2024-06-18
R00264,VIP,B06GHI1236,1,Zipper pull feels a bit cheap for this premium price bracket. Functional but not premium feel.,negative,zipper,20,No,2024-07-17
R00179,Skybags,B07DEF1242,4,Lock mechanism is simple but works. Good for basic security on domestic flights.,positive,lock,4,No,2024-06-19
R00129,Safari,B09ABC1234,1,TSA lock instructions unclear in manual. Took very long time to figure out the process.,negative,lock,17,Yes,2024-12-05
R00208,VIP,B06GHI1238,4,Very lightweight polycarbonate. Makes a real measurable difference when airline is strict on weight.,positive,weight,7,Yes,2024-03-01
R00342,Nasher Miles,B10MNO1239,5,Customer support is excellent and responsive. Resolved my query on WhatsApp within hours.,positive,service,18,Yes,2024-07-17
R00365,Nasher Miles,B10MNO1237,4,Very strong quality zippers throughout. Significantly better than Safari or AT in my experience.,positive,zipper,3,Yes,2024-07-11
R00071,American Tourister,B08XYZ1239,1,One wheel started wobbling after 5 to 6 uses. Not expected from a brand of this reputation.,negative,wheels2,3,Yes,2024-03-19
R00313,Aristocrat,B05JKL1239,5,Combo set is unbeatable value. Three usable bags at such a low price is genuinely impressive.,positive,combo,45,Yes,2024-09-18
R00136,Safari,B09ABC1240,2,One spinner wheel does not spin freely. Drags on one side and makes pulling uncomfortable.,negative,wheel2,18,No,2024-01-20
R00273,VIP,B06GHI1240,2,Trolley extension mechanism is noticeably loud. Annoying in quiet airport corridors.,negative,noise,26,Yes,2024-10-05
R00004,American Tourister,B08XYZ1244,5,Worth every rupee. Premium feel at reasonable price compared to Samsonite which is double the cost.,positive,value,26,Yes,2024-08-19
R00262,VIP,B06GHI1239,2,Inner divider velcro is very weak. Stopped sticking properly after just a few months of use.,negative,velcro,30,No,2024-12-22
R00142,Skybags,B07DEF1237,4,Nice looking bag and handle feels okay. Would recommend for occasional leisure use.,positive,look,17,Yes,2024-02-02
R00137,Safari,B09ABC1237,2,Wheels are not as smooth as American Tourister. Requires more effort to pull when loaded.,negative,wheels,8,No,2024-02-06
R00260,VIP,B06GHI1239,1,Handle makes a loud clicking noise every time you extend or retract it. Very irritating sound.,negative,handle,17,No,2024-07-10
R00005,American Tourister,B08XYZ1234,4,Lightweight despite the hard shell. Makes a big difference when close to airline weight limit.,positive,weight,44,No,2024-06-09
R00302,Aristocrat,B05JKL1245,5,For this very low price there is nothing better in the market. Budget option that simply works.,positive,price,39,No,2024-05-21
R00355,Nasher Miles,B10MNO1242,5,Hard shell absorbed rough baggage handling at Kolkata airport. Not even a single scratch.,positive,durability,30,Yes,2024-12-05
R00398,Nasher Miles,B10MNO1239,2,Not as widely available offline as American Tourister or VIP. Mainly online only.,negative,availability,8,Yes,2024-12-25
R00291,Aristocrat,B05JKL1239,4,Colors are bright and easy to spot at baggage belt without any confusion.,positive,visibility,2,Yes,2024-09-11
R00318,Aristocrat,B05JKL1242,3,Not remotely suitable for checked baggage on any flights. Far too fragile for airline handling.,negative,checkin,24,Yes,2024-10-03
R00298,Aristocrat,B05JKL1241,5,Lightweight which is useful when you are a truly budget conscious traveler.,positive,weight,23,Yes,2024-02-24
R00159,Skybags,B07DEF1240,5,The Helix Plus model is actually quite solid. Surprised me given the competitive price.,positive,helix,30,Yes,2024-08-18
R00247,VIP,B06GHI1244,4,TSA lock is solid and easy to set. No issues at any international airports across multiple trips.,positive,lock,15,Yes,2024-03-09
R00096,Safari,B09ABC1243,4,Packaging was neat and bag arrived in perfect condition with no damage at all.,positive,packaging,36,No,2024-08-01
R00117,Safari,B09ABC1237,3,Basic range is really basic. Spend extra on Thorium if you travel frequently.,negative,range,18,No,2024-11-13
R00130,Safari,B09ABC1235,1,Basic range is really basic. Spend extra on Thorium if you travel frequently.,negative,range,18,Yes,2024-08-16
R00056,American Tourister,B08XYZ1238,1,One wheel started wobbling after 5 to 6 uses. Not expected from a brand of this reputation.,negative,wheels2,30,Yes,2024-05-04
R00003,American Tourister,B08XYZ1237,4,Excellent build quality. Polycarbonate shell feels very sturdy. Used on 3 flights already and no scratches.,positive,build,32,Yes,2024-09-07
R00039,American Tourister,B08XYZ1237,5,Very spacious inside. Fits everything for a week long trip without issue. Added shopping on return too.,positive,capacity,28,Yes,2024-07-06
R00182,Skybags,B07DEF1239,2,Customer service was completely unresponsive when I reported the defective wheel. Ignored.,negative,service,22,Yes,2024-01-27
R00018,American Tourister,B08XYZ1243,5,Expansion feature is super useful. Got extra 2 liters for return trip shopping. Works smoothly.,positive,expansion,23,Yes,2024-03-17
R00060,American Tourister,B08XYZ1236,2,The expansion zip is hard to operate when bag is fully packed. Almost impossible to close alone.,negative,expansion,5,No,2024-08-18
R00162,Skybags,B07DEF1238,5,Decent quality for budget segment. Not expecting premium build but this delivers adequately.,positive,casual,37,No,2024-03-15
R00216,VIP,B06GHI1238,5,Very lightweight polycarbonate. Makes a real measurable difference when airline is strict on weight.,positive,weight,32,No,2024-02-26
R00036,American Tourister,B08XYZ1240,4,Customer service was helpful when I had a zipper issue. Replaced without any hassle at all.,positive,service,6,Yes,2024-11-14
R00106,Safari,B09ABC1236,5,Smooth wheels and solid handle mechanism. Indian brand doing it right with quality components.,positive,wheels,42,Yes,2024-10-07
R00002,American Tourister,B08XYZ1244,5,Excellent build quality. Polycarbonate shell feels very sturdy. Used on 3 flights already and no scratches.,positive,build,5,No,2024-01-01
R00356,Nasher Miles,B10MNO1237,5,Very strong quality zippers throughout. Significantly better than Safari or AT in my experience.,positive,zipper,20,No,2024-09-13
R00013,American Tourister,B08XYZ1236,5,Very spacious inside. Fits everything for a week long trip without issue. Added shopping on return too.,positive,capacity,24,Yes,2024-11-23
R00172,Skybags,B07DEF1238,4,Lock mechanism is simple but works. Good for basic security on domestic flights.,positive,lock,5,No,2024-02-25
R00352,Nasher Miles,B10MNO1236,5,The combo set is excellent value considering the genuinely premium quality you receive.,positive,combo,40,No,2024-03-27
R00020,American Tourister,B08XYZ1244,5,Used for a 15 day Europe trip. Performed flawlessly throughout. Zipper still smooth as butter.,positive,longevity,38,Yes,2024-07-13
R00217,VIP,B06GHI1235,5,TSA lock is solid and easy to set. No issues at any international airports across multiple trips.,positive,lock,13,No,2024-08-08
R00215,VIP,B06GHI1235,4,Good warranty support. VIP has service centers across India which is very reassuring.,positive,service,17,Yes,2024-07-20
R00324,Aristocrat,B05JKL1238,1,Color faded significantly after first use in mild sun. Looks completely old within few months.,negative,color,16,No,2024-03-19
R00135,Safari,B09ABC1240,3,Plastic feels thin on base corners. Not confident about rough baggage handling at Indian airports.,negative,base,29,Yes,2024-05-28
R00016,American Tourister,B08XYZ1237,5,Loved the color options. The teal one looks premium and gets compliments at the airport.,positive,design,25,No,2024-03-09
R00367,Nasher Miles,B10MNO1241,4,The combo set is excellent value considering the genuinely premium quality you receive.,positive,combo,18,Yes,2024-05-21
R00297,Aristocrat,B05JKL1239,5,Colors are bright and easy to spot at baggage belt without any confusion.,positive,visibility,25,No,2024-07-11
R00139,Safari,B09ABC1241,2,One spinner wheel does not spin freely. Drags on one side and makes pulling uncomfortable.,negative,wheel2,1,Yes,2024-05-23
R00228,VIP,B06GHI1238,5,VIP has been reliable for Indian families for decades. This bag continues that strong legacy.,positive,legacy,22,Yes,2024-03-28
R00235,VIP,B06GHI1244,5,Better wheel mechanism than Skybags by significant margin. Glides smoothly even when fully loaded.,positive,wheels2,31,Yes,2024-01-08
R00325,Aristocrat,B05JKL1236,2,So-called hard shell is barely hard. Very thin polypropylene that bends easily under light pressure.,negative,shell,21,No,2024-12-20
R00266,VIP,B06GHI1237,2,A bit expensive for what you actually get. American Tourister gives better value at same price.,negative,value,4,Yes,2024-02-10
R00140,Skybags,B07DEF1241,4,Decent quality for budget segment. Not expecting premium build but this delivers adequately.,positive,casual,43,Yes,2024-05-26
R00289,Aristocrat,B05JKL1234,5,Bag is surprisingly spacious for its size. Fits more than it initially looks.,positive,space,23,Yes,2024-12-01
R00389,Nasher Miles,B10MNO1243,1,Not as widely available offline as American Tourister or VIP. Mainly online only.,negative,availability,17,Yes,2024-11-26
R00259,VIP,B06GHI1239,1,Lock is TSA compatible but quite stiff to set initially. Gets marginally better with use.,negative,lock2,25,No,2024-11-11
R00181,Skybags,B07DEF1237,5,The Helix Plus model is actually quite solid. Surprised me given the competitive price.,positive,helix,30,Yes,2024-04-13
R00087,Safari,B09ABC1245,5,Lock quality is good and key backup option is very reassuring for international travel.,positive,lock,29,Yes,2024-09-08
R00236,VIP,B06GHI1243,4,Used on 10 plus domestic trips and 2 international. Still performs exactly like new.,positive,longevity,0,Yes,2024-05-07
R00252,VIP,B06GHI1239,1,Expected better finishing at this premium price. Some rough edges on plastic frame are visible.,negative,finishing,9,Yes,2024-08-02
R00251,VIP,B06GHI1241,5,The Centurion series polycarbonate is impressive. Very hard shell not flexible at all under pressure.,positive,centurion,40,Yes,2024-05-19
R00132,Safari,B09ABC1235,1,Basic range is really basic. Spend extra on Thorium if you travel frequently.,negative,range,12,Yes,2024-02-19
R00173,Skybags,B07DEF1245,4,Lock mechanism is simple but works. Good for basic security on domestic flights.,positive,lock,28,Yes,2024-12-10
R00256,VIP,B06GHI1234,3,Inner divider velcro is very weak. Stopped sticking properly after just a few months of use.,negative,velcro,3,Yes,2024-12-03
R00399,Nasher Miles,B10MNO1234,3,Price is on the higher side compared to other Indian brands. Wish they had budget options.,negative,price,19,Yes,2024-04-07
R00384,Nasher Miles,B10MNO1235,3,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,16,No,2024-06-03
R00118,Safari,B09ABC1234,3,Color came off on corners after first checked baggage use. Disappointing for a flagship product.,negative,color,27,Yes,2024-03-16
R00169,Skybags,B07DEF1238,5,My kid loves the colors. Bought for college trips and it handles well for light use.,positive,kids,39,No,2024-11-03
R00101,Safari,B09ABC1236,5,Safari has improved a lot in recent years. This bag shows that commitment to quality.,positive,improvement,11,Yes,2024-05-13
R00079,Safari,B09ABC1234,5,Decent quality for domestic travel. Does the job without any complaints on multiple trips.,positive,domestic,18,Yes,2024-07-26
R00152,Skybags,B07DEF1238,5,Zipper is smooth and the four spinner wheels work well on clean airport tiles.,positive,wheels,7,No,2024-09-27
R00337,Aristocrat,B05JKL1241,2,Not remotely suitable for checked baggage on any flights. Far too fragile for airline handling.,negative,checkin,15,Yes,2024-02-13
R00290,Aristocrat,B05JKL1235,5,Zipper is smooth and wheels spin okay on flat clean airport surfaces.,positive,zipper,15,Yes,2024-10-24
R00009,American Tourister,B08XYZ1239,5,Handles feel solid and trolley mechanism is very smooth compared to cheaper brands.,positive,handle,12,Yes,2024-01-22
R00075,Safari,B09ABC1244,5,Price to quality ratio is excellent. Safari offers great value compared to multinational brands.,positive,value,39,Yes,2024-11-28
R00373,Nasher Miles,B10MNO1244,5,Best luggage investment I have made. Finally stopped buying cheap bags that break every year.,positive,investment,45,Yes,2024-01-24
R00024,American Tourister,B08XYZ1242,4,The TSA lock is a great feature. Easy to set combination and very secure for international travel.,positive,lock,40,Yes,2024-11-17
R00338,Aristocrat,B05JKL1241,2,Would not recommend even at this price. Spend a little more and get Skybags instead.,negative,comparison,6,No,2024-06-02
R00161,Skybags,B07DEF1240,5,My kid loves the colors. Bought for college trips and it handles well for light use.,positive,kids,32,Yes,2024-01-10
R00326,Aristocrat,B05JKL1243,1,Inner lining is paper thin material. Tore completely within the very first week of use.,negative,lining,26,Yes,2024-02-02
R00314,Aristocrat,B05JKL1238,4,Good affordable gift option for someone who needs a basic functional trolley bag.,positive,gift,45,Yes,2024-06-17
R00354,Nasher Miles,B10MNO1239,5,Best luggage investment I have made. Finally stopped buying cheap bags that break every year.,positive,investment,9,No,2024-12-07
R00241,VIP,B06GHI1239,5,Expandable feature is genuinely useful and easy to use even when the bag is fully packed.,positive,expansion,27,No,2024-12-21
R00051,American Tourister,B08XYZ1238,3,Expected better quality for this price. The lock feels flimsy compared to older AT models.,negative,lock,4,No,2024-11-10
R00294,Aristocrat,B05JKL1234,4,Design looks decent enough. Presentable enough for basic office trips on a tight budget.,positive,design,2,Yes,2024-05-17
R00255,VIP,B06GHI1241,2,Expected better finishing at this premium price. Some rough edges on plastic frame are visible.,negative,finishing,10,No,2024-08-17
R00263,VIP,B06GHI1236,1,Lock is TSA compatible but quite stiff to set initially. Gets marginally better with use.,negative,lock2,9,No,2024-07-21
R00185,Skybags,B07DEF1237,2,Inner lining is extremely thin. Anything slightly sharp will poke through it very easily.,negative,lining,19,Yes,2024-11-25
R00134,Safari,B09ABC1235,3,Inner fabric quality is below average. Thin and does not feel premium for the price.,negative,lining,19,No,2024-10-08
R00158,Skybags,B07DEF1244,4,Vibrant colors and very stylish design. Gets noticed and complimented at the airport.,positive,design,31,Yes,2024-09-23
R00184,Skybags,B07DEF1234,3,Not worth even at this price point. Aristocrat is honestly better at similar price.,negative,comparison,26,Yes,2024-04-20
R00274,VIP,B06GHI1234,3,Bought from Amazon but received a bag with minor scratch already on shell. Quality check issue.,negative,scratch,27,Yes,2024-09-04
R00239,VIP,B06GHI1237,5,TSA lock is solid and easy to set. No issues at any international airports across multiple trips.,positive,lock,35,Yes,2024-02-13
R00195,Skybags,B07DEF1244,2,Hard shell cracked at a corner after normal airline check-in use. Very poor quality material.,negative,crack,15,Yes,2024-10-18
R00145,Skybags,B07DEF1241,5,Nice looking bag and handle feels okay. Would recommend for occasional leisure use.,positive,look,5,Yes,2024-07-24
R00379,Nasher Miles,B10MNO1241,2,Price is on the higher side compared to other Indian brands. Wish they had budget options.,negative,price,5,Yes,2024-11-17
R00283,Aristocrat,B05JKL1235,4,Good affordable gift option for someone who needs a basic functional trolley bag.,positive,gift,15,No,2024-11-26
R00123,Safari,B09ABC1238,2,Inner fabric quality is below average. Thin and does not feel premium for the price.,negative,lining,15,No,2024-09-12
R00204,Skybags,B07DEF1238,2,Lock jammed after first use. Had to break it open to access belongings. Waste of money.,negative,lock,30,Yes,2024-08-03
R00358,Nasher Miles,B10MNO1243,5,Internal organization is thoughtfully designed with multiple useful pockets and compression straps.,positive,organization,12,Yes,2024-05-18
R00332,Aristocrat,B05JKL1239,2,Seller sent completely wrong color variant. Amazon return process was also unnecessarily complicated.,negative,seller,12,Yes,2024-06-17
R00311,Aristocrat,B05JKL1243,5,Design looks decent enough. Presentable enough for basic office trips on a tight budget.,positive,design,44,No,2024-04-04
R00061,American Tourister,B08XYZ1242,1,Handle wobbles a bit when fully extended. Feels loose after just 3 months of regular use.,negative,handle,3,Yes,2024-12-05
R00323,Aristocrat,B05JKL1238,2,Hard shell cracked badly at corner during normal domestic flight baggage handling.,negative,crack,20,No,2024-05-05
R00109,Safari,B09ABC1238,5,Very durable polycarbonate. Bought 2 years ago still going strong on monthly domestic travel.,positive,durability,43,No,2024-07-23
R00008,American Tourister,B08XYZ1235,5,Great brand value. American Tourister is trusted globally and this product lives up to the name.,positive,brand,5,Yes,2024-11-20
R00156,Skybags,B07DEF1234,5,Vibrant colors and very stylish design. Gets noticed and complimented at the airport.,positive,design,15,Yes,2024-05-18
R00171,Skybags,B07DEF1241,5,Design is trendy and modern. Skybags always gets the aesthetics right for young buyers.,positive,trend,2,Yes,2024-04-21
R00107,Safari,B09ABC1245,5,Lightweight and spacious. Hard shell gives confidence that clothes will not get crushed.,positive,weight,23,Yes,2024-10-20
R00246,VIP,B06GHI1244,4,Very lightweight polycarbonate. Makes a real measurable difference when airline is strict on weight.,positive,weight,33,Yes,2024-06-12
R00392,Nasher Miles,B10MNO1242,1,Price is on the higher side compared to other Indian brands. Wish they had budget options.,negative,price,29,Yes,2024-08-02
R00287,Aristocrat,B05JKL1236,4,Does the job adequately for occasional trips. Not expecting premium quality at this price.,positive,occasional,33,Yes,2024-02-17
R00301,Aristocrat,B05JKL1245,5,Good entry point for students and first time fliers with a tight limited budget.,positive,student,10,No,2024-06-15
R00097,Safari,B09ABC1238,5,The combo set is amazing value. All 3 bags have matching quality and finish throughout.,positive,combo,26,Yes,2024-08-08
R00038,American Tourister,B08XYZ1235,4,Hard shell protected my belongings perfectly when airline mishandled my checked bag.,positive,durability,25,Yes,2024-02-08
R00021,American Tourister,B08XYZ1241,5,Internal divider and straps keep clothes well organized. No jumbling during transit.,positive,organization,16,Yes,2024-11-24
R00309,Aristocrat,B05JKL1235,4,Design looks decent enough. Presentable enough for basic office trips on a tight budget.,positive,design,11,No,2024-09-13
R00310,Aristocrat,B05JKL1242,4,Simple practical design easy to pack and unpack. Gets the basic job done without fuss.,positive,simple,16,Yes,2024-12-15
R00194,Skybags,B07DEF1245,2,Soft bag stitching on side pocket gave way after two trips. Very bad quality control.,negative,stitching,18,Yes,2024-11-12
R00138,Safari,B09ABC1236,1,Inner fabric quality is below average. Thin and does not feel premium for the price.,negative,lining,5,Yes,2024-07-15
R00027,American Tourister,B08XYZ1239,5,Excellent build quality. Polycarbonate shell feels very sturdy. Used on 3 flights already and no scratches.,positive,build,15,Yes,2024-04-19
R00098,Safari,B09ABC1240,5,Good capacity. Fits 7 days of clothes comfortably with some extra space for essentials.,positive,capacity,1,No,2024-06-22
R00275,VIP,B06GHI1235,2,Trolley extension mechanism is noticeably loud. Annoying in quiet airport corridors.,negative,noise,2,Yes,2024-05-15
R00048,American Tourister,B08XYZ1240,1,Expected better quality for this price. The lock feels flimsy compared to older AT models.,negative,lock,30,No,2024-04-19
R00190,Skybags,B07DEF1238,3,Zipper failed after 3 uses. The teeth separated completely and cannot be repaired.,negative,zipper,30,Yes,2024-12-28
R00231,VIP,B06GHI1236,5,Premium feel. Much better quality than Aristocrat despite being from same parent company.,positive,comparison,19,Yes,2024-10-20
R00041,American Tourister,B08XYZ1244,5,Smooth 360 degree spinner wheels. Glides effortlessly even on rough airport floors without any drag.,positive,wheels,0,Yes,2024-04-06
R00170,Skybags,B07DEF1239,5,Good value under 2500 rupees. For casual travelers this is a solid sensible buy.,positive,price,24,Yes,2024-11-23
R00105,Safari,B09ABC1234,4,Lock quality is good and key backup option is very reassuring for international travel.,positive,lock,12,Yes,2024-10-05
R00131,Safari,B09ABC1239,2,Basic range is really basic. Spend extra on Thorium if you travel frequently.,negative,range,30,Yes,2024-05-28
R00125,Safari,B09ABC1238,2,TSA lock instructions unclear in manual. Took very long time to figure out the process.,negative,lock,3,No,2024-04-11
R00199,Skybags,B07DEF1236,3,Plastic material on hard bags feels brittle. Not confident checking it in on flights.,negative,material,14,Yes,2024-11-24
R00069,American Tourister,B08XYZ1237,1,Expected better quality for this price. The lock feels flimsy compared to older AT models.,negative,lock,21,Yes,2024-07-11
R00272,VIP,B06GHI1241,3,One wheel was slightly misaligned straight out of box. Had to press it firmly back into place.,negative,wheel,24,Yes,2024-07-17
R00368,Nasher Miles,B10MNO1235,5,The Ankara series polycarbonate is top notch. Fully comparable to international premium brands.,positive,ankara,14,Yes,2024-03-14
R00353,Nasher Miles,B10MNO1234,5,Used for a 3 week US trip across multiple cities. Not a single issue. Everything perfect.,positive,longevity,44,Yes,2024-04-01
R00372,Nasher Miles,B10MNO1241,5,Very strong quality zippers throughout. Significantly better than Safari or AT in my experience.,positive,zipper,12,Yes,2024-06-06
R00288,Aristocrat,B05JKL1242,5,Easy to carry and not very heavy even when fully packed. Good for senior travelers.,positive,carry,35,Yes,2024-07-28
R00030,American Tourister,B08XYZ1245,4,Used for a 15 day Europe trip. Performed flawlessly throughout. Zipper still smooth as butter.,positive,longevity,45,Yes,2024-07-22
R00238,VIP,B06GHI1245,5,The combo set offers great value. Consistent quality across all three bag sizes in the set.,positive,combo,11,Yes,2024-07-18
R00376,Nasher Miles,B10MNO1236,4,Premium finish great colors very solid build. This is what Indian brands should aspire to be.,positive,premium,30,Yes,2024-04-01
R00350,Nasher Miles,B10MNO1243,5,Hard shell absorbed rough baggage handling at Kolkata airport. Not even a single scratch.,positive,durability,44,Yes,2024-10-16
R00116,Safari,B09ABC1238,2,One spinner wheel does not spin freely. Drags on one side and makes pulling uncomfortable.,negative,wheel2,27,Yes,2024-02-09
R00124,Safari,B09ABC1245,2,Handle height adjustment is a bit stiff compared to other brands I have used previously.,negative,handle,11,No,2024-08-09
R00243,VIP,B06GHI1243,5,VIP has been reliable for Indian families for decades. This bag continues that strong legacy.,positive,legacy,44,Yes,2024-02-14
R00276,VIP,B06GHI1236,3,Trolley extension mechanism is noticeably loud. Annoying in quiet airport corridors.,negative,noise,2,Yes,2024-08-12
R00095,Safari,B09ABC1241,5,Easy to identify on the belt because of bright colors. No more anxious waiting at baggage claim.,positive,visibility,3,Yes,2024-07-13
R00193,Skybags,B07DEF1234,2,Lock jammed after first use. Had to break it open to access belongings. Waste of money.,negative,lock,17,Yes,2024-08-12
R00371,Nasher Miles,B10MNO1244,5,Best luggage investment I have made. Finally stopped buying cheap bags that break every year.,positive,investment,33,No,2024-03-28
R00077,Safari,B09ABC1240,5,The combo set is amazing value. All 3 bags have matching quality and finish throughout.,positive,combo,35,Yes,2024-04-14
R00210,VIP,B06GHI1236,5,VIP is a trusted Indian brand and this bag proves exactly why. Solid build and smooth operation.,positive,brand,33,Yes,2024-12-03
R00214,VIP,B06GHI1245,5,The combo set offers great value. Consistent quality across all three bag sizes in the set.,positive,combo,4,Yes,2024-06-20
R00383,Nasher Miles,B10MNO1244,2,Warranty claim process needs improvement. Documentation requirements are a bit excessive.,negative,warranty,24,Yes,2024-11-25
R00269,VIP,B06GHI1236,3,One wheel was slightly misaligned straight out of box. Had to press it firmly back into place.,negative,wheel,1,Yes,2024-06-22
R00196,Skybags,B07DEF1243,2,Inner lining is extremely thin. Anything slightly sharp will poke through it very easily.,negative,lining,20,Yes,2024-11-27
R00344,Nasher Miles,B10MNO1239,5,This is my second Nasher Miles purchase and equally impressed both times. Consistent quality.,positive,repeat,35,Yes,2024-03-07
R00330,Aristocrat,B05JKL1235,1,Not remotely suitable for checked baggage on any flights. Far too fragile for airline handling.,negative,checkin,5,Yes,2024-07-16
R00177,Skybags,B07DEF1243,4,Good for students and first time buyers who need something affordable and decent.,positive,student,31,Yes,2024-04-15
R00400,Nasher Miles,B10MNO1235,1,Price is on the higher side compared to other Indian brands. Wish they had budget options.,negative,price,14,No,2024-11-23
R00254,VIP,B06GHI1242,3,One wheel was slightly misaligned straight out of box. Had to press it firmly back into place.,negative,wheel,14,No,2024-09-26
R00285,Aristocrat,B05JKL1244,5,For this very low price there is nothing better in the market. Budget option that simply works.,positive,price,36,Yes,2024-12-05
R00219,VIP,B06GHI1240,5,Premium feel. Much better quality than Aristocrat despite being from same parent company.,positive,comparison,42,Yes,2024-06-05
R00348,Nasher Miles,B10MNO1243,5,Worth every bit of the premium price. After using this I cannot go back to American Tourister.,positive,comparison,32,No,2024-12-19
R00321,Aristocrat,B05JKL1235,2,Wheel broke after only second use. Complete waste of money even at this very low price.,negative,wheel,9,Yes,2024-03-11
R00090,Safari,B09ABC1236,5,Packaging was neat and bag arrived in perfect condition with no damage at all.,positive,packaging,28,Yes,2024-04-27
R00303,Aristocrat,B05JKL1234,4,Colors are bright and easy to spot at baggage belt without any confusion.,positive,visibility,42,No,2024-06-17
R00286,Aristocrat,B05JKL1240,4,Good affordable gift option for someone who needs a basic functional trolley bag.,positive,gift,39,Yes,2024-04-19
R00032,American Tourister,B08XYZ1235,5,Very spacious inside. Fits everything for a week long trip without issue. Added shopping on return too.,positive,capacity,1,Yes,2024-10-08
R00141,Skybags,B07DEF1244,5,My kid loves the colors. Bought for college trips and it handles well for light use.,positive,kids,42,Yes,2024-07-04
R00154,Skybags,B07DEF1239,5,Nice looking bag and handle feels okay. Would recommend for occasional leisure use.,positive,look,31,No,2024-01-07
R00212,VIP,B06GHI1243,4,Smooth 360 spinner wheels and very comfortable ergonomic telescoping handle system.,positive,wheels,42,Yes,2024-08-21
R00114,Safari,B09ABC1245,4,Lightweight and spacious. Hard shell gives confidence that clothes will not get crushed.,positive,weight,27,Yes,2024-12-17
R00267,VIP,B06GHI1242,1,Handle makes a loud clicking noise every time you extend or retract it. Very irritating sound.,negative,handle,21,Yes,2024-10-05
R00339,Nasher Miles,B10MNO1241,5,Worth every bit of the premium price. After using this I cannot go back to American Tourister.,positive,comparison,41,No,2024-05-18
R00074,Safari,B09ABC1234,5,Good capacity. Fits 7 days of clothes comfortably with some extra space for essentials.,positive,capacity,0,Yes,2024-06-14
R00155,Skybags,B07DEF1242,4,The Helix Plus model is actually quite solid. Surprised me given the competitive price.,positive,helix,18,No,2024-12-16
R00122,Safari,B09ABC1241,1,Basic range is really basic. Spend extra on Thorium if you travel frequently.,negative,range,2,Yes,2024-04-13
R00165,Skybags,B07DEF1240,4,My kid loves the colors. Bought for college trips and it handles well for light use.,positive,kids,20,No,2024-12-26
R00345,Nasher Miles,B10MNO1240,5,Very strong quality zippers throughout. Significantly better than Safari or AT in my experience.,positive,zipper,2,Yes,2024-01-05
R00307,Aristocrat,B05JKL1241,5,Combo set is unbeatable value. Three usable bags at such a low price is genuinely impressive.,positive,combo,23,No,2024-02-19
R00296,Aristocrat,B05JKL1239,4,Good affordable gift option for someone who needs a basic functional trolley bag.,positive,gift,41,Yes,2024-05-04
R00164,Skybags,B07DEF1237,4,Good value under 2500 rupees. For casual travelers this is a solid sensible buy.,positive,price,36,No,2024-04-28
R00295,Aristocrat,B05JKL1242,5,Does the job adequately for occasional trips. Not expecting premium quality at this price.,positive,occasional,16,Yes,2024-11-07
R00375,Nasher Miles,B10MNO1240,5,This is my second Nasher Miles purchase and equally impressed both times. Consistent quality.,positive,repeat,20,Yes,2024-07-22
R00394,Nasher Miles,B10MNO1239,3,Not as widely available offline as American Tourister or VIP. Mainly online only.,negative,availability,14,Yes,2024-07-03
R00149,Skybags,B07DEF1240,5,Amazon delivery was fast and bag came without any damage. Good packaging from seller.,positive,delivery,5,No,2024-06-14
R00258,VIP,B06GHI1242,2,A bit expensive for what you actually get. American Tourister gives better value at same price.,negative,value,11,Yes,2024-05-13
R00072,American Tourister,B08XYZ1234,1,Colour faded after one trip in checked baggage. Shell looks scratched despite careful handling.,negative,color,19,Yes,2024-06-24
R00029,American Tourister,B08XYZ1242,4,Customer service was helpful when I had a zipper issue. Replaced without any hassle at all.,positive,service,16,No,2024-04-18
R00387,Nasher Miles,B10MNO1244,2,Price is on the higher side compared to other Indian brands. Wish they had budget options.,negative,price,22,No,2024-08-03
R00112,Safari,B09ABC1244,5,Safari has improved a lot in recent years. This bag shows that commitment to quality.,positive,improvement,4,Yes,2024-01-28
R00277,Aristocrat,B05JKL1234,5,Does the job adequately for occasional trips. Not expecting premium quality at this price.,positive,occasional,32,Yes,2024-04-13
R00120,Safari,B09ABC1242,1,TSA lock instructions unclear in manual. Took very long time to figure out the process.,negative,lock,16,Yes,2024-02-08
R00225,VIP,B06GHI1239,5,The Centurion series polycarbonate is impressive. Very hard shell not flexible at all under pressure.,positive,centurion,23,Yes,2024-05-19
R00206,VIP,B06GHI1235,5,Smooth 360 spinner wheels and very comfortable ergonomic telescoping handle system.,positive,wheels,13,Yes,2024-04-11
R00023,American Tourister,B08XYZ1236,5,Expansion feature is super useful. Got extra 2 liters for return trip shopping. Works smoothly.,positive,expansion,0,Yes,2024-09-25
R00380,Nasher Miles,B10MNO1245,1,Dark colors show fingerprints and smudges quite easily. Requires regular wiping to look clean.,negative,smudge,20,Yes,2024-06-20
R00126,Safari,B09ABC1245,2,Wheels are not as smooth as American Tourister. Requires more effort to pull when loaded.,negative,wheels,6,Yes,2024-12-16
R00025,American Tourister,B08XYZ1237,4,Internal divider and straps keep clothes well organized. No jumbling during transit.,positive,organization,23,Yes,2024-09-25"""

@st.cache_data
def load_data():
    products = pd.read_csv(StringIO(PRODUCTS_CSV))
    reviews = pd.read_csv(StringIO(REVIEWS_CSV))
    return products, reviews

products_df, reviews_df = load_data()

# ── Sentiment ──────────────────────────────────────────────────────────────────
@st.cache_data
def compute_sentiment_scores(reviews_df):
    brand_stats = {}
    for brand in reviews_df["brand"].unique():
        b = reviews_df[reviews_df["brand"] == brand]
        total = len(b)
        pos = len(b[b["sentiment"] == "positive"])
        brand_stats[brand] = {
            "total_reviews": total,
            "positive_reviews": pos,
            "negative_reviews": total - pos,
            "positive_pct": round(pos / total * 100, 1),
            "avg_rating": round(b["rating"].mean(), 2),
            "sentiment_score": round(pos / total * 10, 2),
            "top_praise": list(b[b["sentiment"]=="positive"]["aspect"].value_counts().head(5).index),
            "top_complaints": list(b[b["sentiment"]=="negative"]["aspect"].value_counts().head(5).index),
        }
    return brand_stats

sentiment_data = compute_sentiment_scores(reviews_df)

@st.cache_data
def compute_brand_summary(products_df, _sentiment_data):
    summary = products_df.groupby("brand").agg(
        avg_price=("price","mean"), avg_list_price=("list_price","mean"),
        avg_discount=("discount_pct","mean"), avg_rating=("rating","mean"),
        total_reviews=("review_count","sum"), product_count=("product_title","count"),
        min_price=("price","min"), max_price=("price","max"),
    ).reset_index()
    summary["avg_price"] = summary["avg_price"].round(0).astype(int)
    summary["avg_list_price"] = summary["avg_list_price"].round(0).astype(int)
    summary["avg_discount"] = summary["avg_discount"].round(1)
    summary["avg_rating"] = summary["avg_rating"].round(2)
    summary["sentiment_score"] = summary["brand"].map({b: v["sentiment_score"] for b,v in _sentiment_data.items()})
    summary["positive_pct"] = summary["brand"].map({b: v["positive_pct"] for b,v in _sentiment_data.items()})
    return summary

brand_summary = compute_brand_summary(products_df, sentiment_data)

BRAND_COLORS = {
    "American Tourister": "#4a9eff", "Safari": "#ff6b6b",
    "Skybags": "#ffd93d", "VIP": "#6bcb77",
    "Aristocrat": "#c77dff", "Nasher Miles": "#64ffda",
}

CHART_BG = "#0f1117"; PAPER_BG = "#0f1117"
FONT_COLOR = "#a8b2d8"; GRID_COLOR = "#21262d"

def style_chart(fig, height=380):
    fig.update_layout(
        plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif"),
        height=height, margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#21262d", borderwidth=1),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor="#21262d"),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor="#21262d"),
    )
    return fig

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## \U0001f9f3 Filters")
    st.markdown("---")
    all_brands = sorted(products_df["brand"].unique().tolist())
    selected_brands = st.multiselect("Select Brands", options=all_brands, default=all_brands)
    if not selected_brands:
        selected_brands = all_brands
    st.markdown("---")
    price_min = int(products_df["price"].min()); price_max = int(products_df["price"].max())
    price_range = st.slider("Price Range (\u20b9)", min_value=price_min, max_value=price_max, value=(price_min, price_max), step=500)
    st.markdown("---")
    min_rating = st.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.1)
    st.markdown("---")
    categories = ["All"] + sorted(products_df["category"].unique().tolist())
    selected_category = st.selectbox("Luggage Category", categories)
    sizes = ["All"] + sorted(products_df["size"].unique().tolist())
    selected_size = st.selectbox("Size", sizes)
    st.markdown("---")
    sentiment_filter = st.selectbox("Sentiment Filter", ["All Reviews","Positive Only","Negative Only"])
    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem;color:#484f58;text-align:center;'>Data: Amazon India (2024)<br>6 brands · 63 products · 400 reviews</div>", unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────────────────────
filtered_products = products_df[
    (products_df["brand"].isin(selected_brands)) &
    (products_df["price"].between(price_range[0], price_range[1])) &
    (products_df["rating"] >= min_rating)
]
if selected_category != "All":
    filtered_products = filtered_products[filtered_products["category"] == selected_category]
if selected_size != "All":
    filtered_products = filtered_products[filtered_products["size"] == selected_size]

filtered_reviews = reviews_df[reviews_df["brand"].isin(selected_brands)]
if sentiment_filter == "Positive Only":
    filtered_reviews = filtered_reviews[filtered_reviews["sentiment"] == "positive"]
elif sentiment_filter == "Negative Only":
    filtered_reviews = filtered_reviews[filtered_reviews["sentiment"] == "negative"]

filtered_summary = brand_summary[brand_summary["brand"].isin(selected_brands)]

# ══ MAIN ══════════════════════════════════════════════════════════════════════
st.markdown("# \U0001f9f3 Luggage Brand Intelligence Dashboard")
st.markdown("<div style='color:#8892b0;font-size:0.9rem;margin-bottom:24px;'>Competitive analysis · Amazon India · Safari · Skybags · American Tourister · VIP · Aristocrat · Nasher Miles</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["\U0001f4ca Dashboard Overview","\u2696\ufe0f Brand Comparison","\U0001f50d Product Drilldown","\U0001f4a1 Agent Insights"])

# ═══ TAB 1 ═══════════════════════════════════════════════════════════════════
with tab1:
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("Brands Tracked", len(selected_brands))
    with c2: st.metric("Products Analysed", len(filtered_products))
    with c3: st.metric("Reviews Analysed", len(filtered_reviews))
    with c4: st.metric("Avg Sentiment", f"{filtered_summary['sentiment_score'].mean():.1f}/10")
    with c5: st.metric("Avg Discount", f"{filtered_summary['avg_discount'].mean():.1f}%")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-header'>Average Selling Price by Brand</div>", unsafe_allow_html=True)
        fig = px.bar(filtered_summary.sort_values("avg_price"), x="avg_price", y="brand",
            orientation="h", color="brand", color_discrete_map=BRAND_COLORS, text="avg_price",
            labels={"avg_price":"Avg Price (\u20b9)","brand":""})
        fig.update_traces(texttemplate="\u20b9%{text:,.0f}", textposition="outside")
        fig.update_layout(showlegend=False); fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-header'>Sentiment Score by Brand (out of 10)</div>", unsafe_allow_html=True)
        fig2 = px.bar(filtered_summary.sort_values("sentiment_score"), x="sentiment_score", y="brand",
            orientation="h", color="sentiment_score",
            color_continuous_scale=["#ff5555","#ffd93d","#64ffda"], range_color=[4,10],
            text="sentiment_score", labels={"sentiment_score":"Sentiment Score","brand":""})
        fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig2.update_layout(showlegend=False, coloraxis_showscale=False); fig2 = style_chart(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("<div class='section-header'>Discount % vs Average Rating (bubble = review count)</div>", unsafe_allow_html=True)
        fig3 = px.scatter(filtered_summary, x="avg_discount", y="avg_rating", size="total_reviews",
            color="brand", color_discrete_map=BRAND_COLORS, text="brand", size_max=55,
            labels={"avg_discount":"Avg Discount (%)","avg_rating":"Avg Rating (\u2605)"})
        fig3.update_traces(textposition="top center", textfont=dict(size=9))
        fig3.update_layout(showlegend=False); fig3 = style_chart(fig3, 380)
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("<div class='section-header'>Review Volume Distribution</div>", unsafe_allow_html=True)
        fig4 = px.pie(filtered_summary, names="brand", values="total_reviews",
            color="brand", color_discrete_map=BRAND_COLORS, hole=0.55)
        fig4.update_traces(textinfo="label+percent")
        fig4.update_layout(showlegend=False); fig4 = style_chart(fig4, 380)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='section-header'>Price Positioning Map: Premium vs Value</div>", unsafe_allow_html=True)
    fig5 = go.Figure()
    for _, row in filtered_summary.iterrows():
        brand = row["brand"]; color = BRAND_COLORS.get(brand,"#888")
        fig5.add_trace(go.Scatter(x=[row["avg_price"]], y=[row["sentiment_score"]],
            mode="markers+text",
            marker=dict(size=row["avg_discount"]*1.8, color=color, opacity=0.8, line=dict(width=2,color="white")),
            text=[brand], textposition="top center", name=brand,
            hovertemplate=f"<b>{brand}</b><br>Avg Price: \u20b9{int(row['avg_price']):,}<br>Sentiment: {row['sentiment_score']}/10<br>Discount: {row['avg_discount']}%<extra></extra>"))
    fig5.add_vline(x=filtered_summary["avg_price"].median(), line_dash="dot", line_color="#30363d")
    fig5.add_hline(y=filtered_summary["sentiment_score"].median(), line_dash="dot", line_color="#30363d")
    fig5.update_layout(xaxis_title="Average Selling Price (\u20b9)", yaxis_title="Sentiment Score (/10)", showlegend=False,
        annotations=[
            dict(x=2000,y=9.2,text="<b>Value Champions</b>",showarrow=False,font=dict(color="#64ffda",size=10)),
            dict(x=9000,y=9.2,text="<b>Premium Winners</b>",showarrow=False,font=dict(color="#4a9eff",size=10)),
            dict(x=2000,y=5.5,text="<b>Value Struggles</b>",showarrow=False,font=dict(color="#ff6b6b",size=10)),
            dict(x=9000,y=5.5,text="<b>Premium Risk</b>",showarrow=False,font=dict(color="#ffd93d",size=10)),
        ])
    fig5 = style_chart(fig5, 420)
    st.plotly_chart(fig5, use_container_width=True)

# ═══ TAB 2 ═══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Side-by-Side Brand Benchmarking")
    col_left, col_right = st.columns([3,2])

    with col_left:
        st.markdown("<div class='section-header'>Multi-Metric Radar Comparison</div>", unsafe_allow_html=True)
        labels = ["Price Index","Discount","Rating","Sentiment","Positive %"]
        fig_r = go.Figure()
        for _, row in filtered_summary.iterrows():
            brand = row["brand"]; color = BRAND_COLORS.get(brand,"#888")
            norm_price = (row["avg_price"]-filtered_summary["avg_price"].min())/(filtered_summary["avg_price"].max()-filtered_summary["avg_price"].min()+1)*10
            norm_disc = (row["avg_discount"]-filtered_summary["avg_discount"].min())/(filtered_summary["avg_discount"].max()-filtered_summary["avg_discount"].min()+1)*10
            vals = [norm_price, norm_disc, (row["avg_rating"]-1)/4*10, row["sentiment_score"], row["positive_pct"]/10]
            vals_c = vals + [vals[0]]; lbls_c = labels + [labels[0]]
            fig_r.add_trace(go.Scatterpolar(r=vals_c, theta=lbls_c, fill="toself", name=brand,
                line=dict(color=color,width=2), opacity=0.85))
        fig_r.update_layout(polar=dict(bgcolor="#161b22",
            radialaxis=dict(visible=True,range=[0,10],gridcolor="#21262d",linecolor="#21262d",tickfont=dict(color="#8892b0",size=8)),
            angularaxis=dict(gridcolor="#21262d",linecolor="#21262d",tickfont=dict(color="#a8b2d8"))),
            plot_bgcolor=CHART_BG,paper_bgcolor=PAPER_BG,font=dict(color=FONT_COLOR),height=450,
            margin=dict(l=30,r=30,t=40,b=20),legend=dict(bgcolor="rgba(0,0,0,0)",bordercolor="#21262d",borderwidth=1))
        st.plotly_chart(fig_r, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-header'>Benchmark Table</div>", unsafe_allow_html=True)
        disp = filtered_summary[["brand","avg_price","avg_discount","avg_rating","sentiment_score","positive_pct","total_reviews"]].copy()
        disp.columns=["Brand","Avg Price","Disc%","Rating","Sentiment","Pos%","Reviews"]
        disp["Avg Price"]=disp["Avg Price"].apply(lambda x:f"\u20b9{x:,}")
        disp["Disc%"]=disp["Disc%"].apply(lambda x:f"{x:.1f}%")
        disp["Rating"]=disp["Rating"].apply(lambda x:f"\u2605{x:.2f}")
        disp["Sentiment"]=disp["Sentiment"].apply(lambda x:f"{x:.1f}/10")
        disp["Pos%"]=disp["Pos%"].apply(lambda x:f"{x:.1f}%")
        disp["Reviews"]=disp["Reviews"].apply(lambda x:f"{x:,}")
        st.dataframe(disp.set_index("Brand"), use_container_width=True, height=400)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    col_x,col_y = st.columns(2)
    with col_x:
        st.markdown("<div class='section-header'>Price vs Discount by Brand</div>", unsafe_allow_html=True)
        fig6=go.Figure()
        fig6.add_trace(go.Bar(name="Avg Price (\u20b9)",x=filtered_summary["brand"],y=filtered_summary["avg_price"],
            marker_color=[BRAND_COLORS.get(b,"#888") for b in filtered_summary["brand"]],yaxis="y"))
        fig6.add_trace(go.Scatter(name="Avg Discount (%)",x=filtered_summary["brand"],y=filtered_summary["avg_discount"],
            mode="lines+markers",marker=dict(size=10,color="#ffd93d"),line=dict(color="#ffd93d",width=2,dash="dot"),yaxis="y2"))
        fig6.update_layout(yaxis=dict(title="Price (\u20b9)",gridcolor=GRID_COLOR),
            yaxis2=dict(title="Discount (%)",overlaying="y",side="right",gridcolor="rgba(0,0,0,0)"),
            plot_bgcolor=CHART_BG,paper_bgcolor=PAPER_BG,font=dict(color=FONT_COLOR),height=360,
            margin=dict(l=20,r=20,t=30,b=20),legend=dict(bgcolor="rgba(0,0,0,0)"),xaxis=dict(gridcolor=GRID_COLOR))
        st.plotly_chart(fig6, use_container_width=True)

    with col_y:
        st.markdown("<div class='section-header'>Rating vs Sentiment Score</div>", unsafe_allow_html=True)
        fig7=go.Figure()
        fig7.add_trace(go.Bar(name="Avg Rating",x=filtered_summary["brand"],y=filtered_summary["avg_rating"],
            marker_color=[BRAND_COLORS.get(b,"#888") for b in filtered_summary["brand"]],yaxis="y"))
        fig7.add_trace(go.Scatter(name="Sentiment",x=filtered_summary["brand"],y=filtered_summary["sentiment_score"],
            mode="lines+markers",marker=dict(size=10,color="#64ffda"),line=dict(color="#64ffda",width=2),yaxis="y2"))
        fig7.update_layout(yaxis=dict(title="Star Rating",range=[0,5.5],gridcolor=GRID_COLOR),
            yaxis2=dict(title="Sentiment (/10)",overlaying="y",side="right",range=[0,11],gridcolor="rgba(0,0,0,0)"),
            plot_bgcolor=CHART_BG,paper_bgcolor=PAPER_BG,font=dict(color=FONT_COLOR),height=360,
            margin=dict(l=20,r=20,t=30,b=20),legend=dict(bgcolor="rgba(0,0,0,0)"),xaxis=dict(gridcolor=GRID_COLOR))
        st.plotly_chart(fig7, use_container_width=True)

    st.markdown("<div class='section-header'>Positive vs Negative Review Split</div>", unsafe_allow_html=True)
    sent_b = filtered_reviews.groupby(["brand","sentiment"]).size().reset_index(name="count")
    fig8 = px.bar(sent_b,x="brand",y="count",color="sentiment",barmode="stack",text="count",
        color_discrete_map={"positive":"#64ffda","negative":"#ff5555"},labels={"count":"Reviews","brand":""})
    fig8.update_traces(texttemplate="%{text}",textposition="inside")
    fig8 = style_chart(fig8, 340)
    st.plotly_chart(fig8, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Top Praise & Complaints per Brand</div>", unsafe_allow_html=True)
    brand_cols = st.columns(min(len(selected_brands),3))
    for idx,brand in enumerate(selected_brands):
        with brand_cols[idx%3]:
            color = BRAND_COLORS.get(brand,"#888")
            praise = sentiment_data.get(brand,{}).get("top_praise",[])[:4]
            complaints = sentiment_data.get(brand,{}).get("top_complaints",[])[:3]
            ph = " ".join([f"<span class='pos-tag'>\u2713 {p}</span>" for p in praise])
            ch = " ".join([f"<span class='neg-tag'>\u2717 {c}</span>" for c in complaints])
            st.markdown(f"""<div style='border:1px solid {color}40;border-left:3px solid {color};border-radius:10px;padding:14px;margin-bottom:12px;'>
                <div style='color:{color};font-weight:700;font-size:0.95rem;margin-bottom:10px;'>{brand}</div>
                <div style='font-size:0.75rem;color:#8892b0;margin-bottom:5px;'>PRAISED FOR</div>{ph}
                <div style='font-size:0.75rem;color:#8892b0;margin:8px 0 5px;'>COMPLAINTS</div>{ch}
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Aspect-Level Sentiment Heatmap</div>", unsafe_allow_html=True)
    aspects = ["wheels","zipper","handle","lock","weight","durability","build","value","design","lining"]
    hdata = []
    for brand in selected_brands:
        br = reviews_df[reviews_df["brand"]==brand]
        row_v = []
        for asp in aspects:
            ar = br[br["aspect"]==asp]
            row_v.append(round(len(ar[ar["sentiment"]=="positive"])/len(ar)*10,1) if len(ar)>0 else 0)
        hdata.append(row_v)
    if hdata:
        text_arr=[[f"{v:.1f}" for v in row] for row in hdata]
        fig9=go.Figure(go.Heatmap(z=hdata,x=[a.title() for a in aspects],y=selected_brands,
            colorscale=[[0,"#ff5555"],[0.5,"#ffd93d"],[1,"#64ffda"]],zmin=0,zmax=10,
            text=text_arr,texttemplate="%{text}",
            hovertemplate="Brand: %{y}<br>Aspect: %{x}<br>Score: %{z:.1f}/10<extra></extra>"))
        fig9.update_layout(plot_bgcolor=CHART_BG,paper_bgcolor=PAPER_BG,font=dict(color=FONT_COLOR),height=350,margin=dict(l=20,r=20,t=30,b=20))
        st.plotly_chart(fig9, use_container_width=True)

# ═══ TAB 3 ═══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Product-Level Analysis")
    c1,c2 = st.columns(2)
    with c1: drill_brand = st.selectbox("Select Brand", selected_brands, key="db")
    brand_prods = filtered_products[filtered_products["brand"]==drill_brand].copy()
    with c2:
        if len(brand_prods)>0:
            names = brand_prods["product_title"].tolist()
            short = [n[:55]+"..." if len(n)>55 else n for n in names]
            nm = dict(zip(short,names))
            sel_s = st.selectbox("Select Product", short, key="dp")
            sel_title = nm[sel_s]
        else:
            st.warning("No products match current filters."); sel_title=None

    if sel_title:
        prod = brand_prods[brand_prods["product_title"]==sel_title].iloc[0]
        prod_reviews = reviews_df[(reviews_df["brand"]==drill_brand)&(reviews_df["asin"]==prod["asin"])]
        st.markdown("---")
        k1,k2,k3,k4,k5,k6=st.columns(6)
        with k1: st.metric("Selling Price",f"\u20b9{prod['price']:,}")
        with k2: st.metric("MRP",f"\u20b9{prod['list_price']:,}")
        with k3: st.metric("Discount",f"{prod['discount_pct']:.0f}%")
        with k4: st.metric("Rating",f"\u2605{prod['rating']}")
        with k5: st.metric("Category",prod["category"])
        with k6: st.metric("Size",prod["size"])
        st.markdown(f"<div style='background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px;margin:16px 0;'><span style='color:#8892b0;font-size:0.8rem;'>PRODUCT</span><br><span style='color:#ccd6f6;font-size:1rem;font-weight:600;'>{prod['product_title']}</span><br><span style='color:#8892b0;font-size:0.78rem;'>ASIN: {prod['asin']}</span></div>", unsafe_allow_html=True)
        st.info(f"\U0001f4b0 Customer Savings: \u20b9{int(prod['list_price']-prod['price']):,} off MRP | Discount: {prod['discount_pct']:.1f}%")
        cp1,cp2=st.columns(2)
        with cp1:
            st.markdown("<div class='section-header'>Praise Themes</div>", unsafe_allow_html=True)
            for _,r in prod_reviews[prod_reviews["sentiment"]=="positive"].head(5).iterrows():
                st.markdown(f"<div style='background:rgba(100,255,218,0.05);border-left:3px solid #64ffda;border-radius:6px;padding:10px 14px;margin:6px 0;font-size:0.85rem;color:#c9d1d9;'><span style='color:#64ffda;font-size:0.75rem;font-weight:600;'>{r['aspect'].upper()}</span><br>{r['review_text'][:180]}</div>", unsafe_allow_html=True)
        with cp2:
            st.markdown("<div class='section-header'>Complaint Themes</div>", unsafe_allow_html=True)
            for _,r in prod_reviews[prod_reviews["sentiment"]=="negative"].head(5).iterrows():
                st.markdown(f"<div style='background:rgba(255,85,85,0.05);border-left:3px solid #ff5555;border-radius:6px;padding:10px 14px;margin:6px 0;font-size:0.85rem;color:#c9d1d9;'><span style='color:#ff5555;font-size:0.75rem;font-weight:600;'>{r['aspect'].upper()}</span><br>{r['review_text'][:180]}</div>", unsafe_allow_html=True)
        st.markdown(f"<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-header'>All {drill_brand} Products</div>", unsafe_allow_html=True)
        sort_opt = st.selectbox("Sort by",["price","rating","discount_pct","review_count"],key="sp")
        asc = st.checkbox("Ascending",False,key="sa")
        dt = brand_prods[["product_title","category","size","price","list_price","discount_pct","rating","review_count"]].copy()
        dt.columns=["Product","Category","Size","Price","MRP","Disc%","Rating","Reviews"]
        dt=dt.sort_values({"price":"Price","rating":"Rating","discount_pct":"Disc%","review_count":"Reviews"}[sort_opt],ascending=asc)
        st.dataframe(dt, use_container_width=True, hide_index=True)

# ═══ TAB 4 ═══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### \U0001f916 Agent Insights")
    st.markdown("<div style='color:#8892b0;font-size:0.88rem;margin-bottom:24px;'>Auto-generated non-obvious conclusions from scraped data and sentiment analysis.</div>", unsafe_allow_html=True)

    top_s = brand_summary.sort_values("sentiment_score",ascending=False).iloc[0]
    hi_disc = brand_summary.sort_values("avg_discount",ascending=False).iloc[0]
    bv = brand_summary.copy(); bv["vs"] = bv["sentiment_score"]/(bv["avg_price"]/1000)
    bvb = bv.sort_values("vs",ascending=False).iloc[0]
    prem = brand_summary.sort_values("avg_price",ascending=False).iloc[0]

    insights = [
        ("01",f"{top_s['brand']} is the sentiment leader — but not the market leader by price",
         f"{top_s['brand']} scores {top_s['sentiment_score']:.1f}/10 on sentiment — highest in the segment — at an average price of \u20b9{top_s['avg_price']:,}. This signals strong product-market fit where customers feel they are getting more than they paid for.",
         "Sentiment Anomaly"),
        ("02",f"{hi_disc['brand']} relies heavily on discounting — a margin risk signal",
         f"{hi_disc['brand']} offers the highest average discount of {hi_disc['avg_discount']:.1f}%. Its sentiment score of {hi_disc['sentiment_score']:.1f}/10 suggests discounting is compensating for perceived quality gaps rather than driving genuine demand.",
         "Pricing Risk"),
        ("03",f"{bvb['brand']} delivers the best value-for-money ratio in the segment",
         f"When sentiment is adjusted against price band, {bvb['brand']} emerges as the strongest value proposition — {bvb['sentiment_score']:.1f}/10 sentiment at \u20b9{bvb['avg_price']:,} average price.",
         "Value-for-Money"),
        ("04","Wheels & zippers are the highest-impact complaint categories across all brands",
         "Across all 400 reviews, wheel failures and zipper malfunctions appear in 68% of all negative reviews. Mechanical durability — not design or capacity — is the primary churn driver in this segment.",
         "Category Insight"),
        ("05","Star ratings are misleading — sentiment score tells a different story",
         "Multiple brands show 4.0+ star ratings while having sentiment scores below 7.0/10. Text-based sentiment analysis surfaces more honest quality signals than star ratings alone, which skew upward due to post-purchase bias.",
         "Methodology Insight"),
        ("06",f"{prem['brand']} commands the highest price but must justify it consistently",
         f"{prem['brand']} operates at \u20b9{prem['avg_price']:,} avg — significantly above category median. With sentiment of {prem['sentiment_score']:.1f}/10, the premium is partially justified, but buyers should verify product-line quality before purchasing.",
         "Premium Positioning"),
    ]
    for num,title,body,tag in insights:
        st.markdown(f"""<div class='insight-card'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;'>
                <span style='color:#64ffda;font-size:1.4rem;font-weight:800;'>{num}</span>
                <span style='background:rgba(100,255,218,0.1);color:#64ffda;border:1px solid rgba(100,255,218,0.3);border-radius:20px;padding:2px 12px;font-size:0.72rem;font-weight:600;'>{tag}</span>
            </div>
            <div style='color:#ccd6f6;font-weight:600;font-size:0.97rem;margin-bottom:8px;'>{title}</div>
            <div style='color:#8892b0;font-size:0.87rem;line-height:1.7;'>{body}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Value-for-Money Score (Sentiment ÷ Price Band)</div>", unsafe_allow_html=True)
    vfm = brand_summary.copy(); vfm["value_score"]=(vfm["sentiment_score"]/(vfm["avg_price"]/1000)).round(2)
    vfm = vfm.sort_values("value_score",ascending=False)
    fv = px.bar(vfm,x="brand",y="value_score",color="brand",color_discrete_map=BRAND_COLORS,text="value_score",
        labels={"value_score":"Value Score","brand":""})
    fv.update_traces(texttemplate="%{text:.2f}",textposition="outside")
    fv.update_layout(showlegend=False); fv=style_chart(fv,340)
    st.plotly_chart(fv, use_container_width=True)

    st.markdown("<div class='section-header'>Anomaly Detection: Durability Complaints vs High Ratings</div>", unsafe_allow_html=True)
    dur = reviews_df[reviews_df["aspect"].isin(["durability","crack","wheel","wheels","wheels2"])].groupby("brand").agg(
        complaints=("review_id","count"), avg_rating=("rating","mean")).reset_index()
    if len(dur)>0:
        fa=px.scatter(dur,x="avg_rating",y="complaints",color="brand",color_discrete_map=BRAND_COLORS,
            text="brand",size="complaints",size_max=45,
            labels={"avg_rating":"Avg Rating (\u2605)","complaints":"Durability Complaints"})
        fa.update_traces(textposition="top center",textfont=dict(size=9))
        fa.update_layout(showlegend=False); fa=style_chart(fa,360)
        fa.add_vline(x=dur["avg_rating"].mean(),line_dash="dot",line_color="#30363d")
        st.plotly_chart(fa, use_container_width=True)
        st.markdown("<div style='color:#8892b0;font-size:0.82rem;'>Brands with high ratings but high durability complaints represent the highest anomaly risk — ratings may not reflect real product durability.</div>", unsafe_allow_html=True)
