import streamlit as st
import pandas as pd
import math
from pathlib import Path


import matplotlib.pyplot as mpl
import matplotlib.colors as mcolors
import seaborn as sb

import numpy as np
import pandas as pd

# kustomisasi nama tab di browser
st.set_page_config(
    page_title='2013-2017 Beijing PRSA stations according to WHO Air Quality Guidelines',
    page_icon=':toolbox:', 
)

# Set the title that appears at the top of the page.
'''
# :toolbox: BEIJING'S POLLUTANT IN DATA (2013-2017)
## <==== klo mau sembunyiin polutan yg gapenting, setting di dashboard kiri y. 


'''

'''
**DATA SOURCE**:  
The data is from
https://www.kaggle.com/datasets/sid321axn/beijing-multisite-airquality-data-set,
and i discovered it from Dicoding's "Belajar Analisis Data dengan Python" course :>

'''

# Add some spacing
''
''

st.markdown(
    """
    cara artiin heatmap & stacked bar chart:
    | warna  | kriteria  |
    |-----------|-----------|
    |<span style="background-color: #A6D75B; color: #000;">A6D75B</span> |  **0**< x < AQG Level      |
    | <span style="background-color: #E07A5F; color: #000;">E07A5F</span>    | **AQG Level** < x < Interim Target 4       |
    | <span style="background-color: #D07666; color: #000;">D07666</span>  | **Interim Target 4** < x <Interim Target 3    |
    | <span style="background-color: #B85042; color: #000;">B85042</span>   | **Interim Target 3** < x <Interim Target 2    |
    | <span style="background-color: #7A3E2F; color: #000;">7A3E2F</span>  | **Interim Target 2** < x <Interim Target 1   |
    | <span style="background-color: #332D2D; color: #000;">332D2D</span>  | **Interim Target 1** < x   |
    """
, unsafe_allow_html=True
)

#========================== perkara NGIMPOR DATA JILID 1 BUAT DATAVIZ ==========================


@st.cache_data
def load_data():
    df = pd.read_csv('dashboard/cleaned_data_semua_area.csv')
    return df

cleaned_data_semua_area = load_data()



# Get unique stations
key_stasiun_data = cleaned_data_semua_area["station"].unique()
key_polutan_data = ["CO","NO2","O3", "PM10", "PM2.5", "SO2" ]



#========================== perkara color pallete ==========================



# 🎨 Generate Unique Colors for Stations
station_colors = [mcolors.to_hex(c) for c in mpl.cm.viridis(np.linspace(0, 1, len(key_stasiun_data)))]
station_color_map = dict(zip(key_stasiun_data, station_colors))

# 🎨 Generate Unique Colors for Pollutants (Using Plasma Palette)
pollutant_colors = [mcolors.to_hex(c) for c in mpl.cm.plasma(np.linspace(0, 1, len(key_polutan_data)))]
pollutant_color_map = dict(zip(key_polutan_data, pollutant_colors))

# 🎨 color pallete buat standar WHO
palet_jojo = ["#A6D75B", "#E07A5F", "#D07666", "#B85042", "#7A3E2F", "#332D2D"]
bin_labels = [
    "1: di bawah AQG",
    "2: di bawah IT4",
    "3: di bawah IT3",
    "4: di bawah IT2",
    "5: di bawah IT1",
    "6: di atas IT1"
]

st.write("pilih mau liat polutan mana :D")
#========================== perkara NGIMPOR DATA JILID 2 BUAT grafik  ==========================

#====== ini buat stacked bar chart yg di dalem tab
@st.cache_data
def baca_csv_stackedbarchart_yang(pollutant_name):
   
    file_path = Path(f'dashboard/summary_stackedbarchart_{pollutant_name}.csv')
    if file_path.exists():
        df = pd.read_csv(file_path)
        return df
    else:
        st.error(f"Data for {pollutant_name} gaada woy :c.")
        return pd.DataFrame()

semuaan_stackedbarchart = {}
for tiap_polutan in key_polutan_data:
    semuaan_stackedbarchart[tiap_polutan] = baca_csv_stackedbarchart_yang(tiap_polutan)



@st.cache_data
def baca_who():
    df = pd.read_csv('dashboard/standar_who.csv')
    return df

standar_who_ok = baca_who()


#========================== perkara bikin helper function2 yg bisa di-call buat bikin grafik ==========================

#-----------------------------------------
#--- stacked bar chart di dalem tab
def stacked_bar_chart_urut( polutannya, datanya, standar_binnya, label_binnya, palet_warnanya):
    
    
    temp_pivoted_data = datanya.set_index("station")
    ax = temp_pivoted_data.plot(
        kind='bar',
        stacked=True,
        figsize=(10, 7),
        color=palet_warnanya,
        title= tiap_polutan
    )

    ax.legend(
        title='TIngkat Keparahan', 
        loc='center left', 
        bbox_to_anchor=(1, 0.5)
    )
    
    mpl.ylabel("Count of Days")
    mpl.xticks(rotation=45, ha='right')
    mpl.tight_layout()
    
    fig = ax.get_figure()

    return fig, ax 


#-----------------------------------------
#--- heatmap di dalem tab
def heatmap_station_polutan(axnya, datanya, individunya, kategorinya, colormapnya, normalisasinya, show_cbar=False):
    pivot = datanya.pivot_table(index="year", columns="datestamp", values=kategorinya)
    mask = pivot.isna() 
    

    sb.heatmap(
        pivot, ax=axnya, cmap=colormapnya, linewidths=0, linecolor=None, norm=normalisasinya, mask=mask, cbar=show_cbar, cbar_kws={'label': pollutant} if show_cbar else None
    )

    axnya.set_title(f"{individunya}", fontsize=10)
    axnya.set_xlabel("")
    axnya.set_ylabel("")

    axnya.set_xticks(np.linspace(15, 365, 12))  # Approx. middle of each month
    axnya.set_xticklabels(
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        rotation=45,
        ha='right',
        fontsize=8
    )
    axnya.tick_params(axis='y', labelsize=8)


#-----------------------------------------
#--- scatterplot timeline di paling atas tab
def scatterplot_timeline(axnya, datanya, yg_digambarnya, colormapnya):
    sb.scatterplot(
        data=datanya, 
        x="daystamp", 
        y=yg_digambarnya, 
        hue="station", 
        alpha=0.6, 
        palette=colormapnya, 
        ax=axnya
    )
    axnya.set_title(f"Konsentrasi {yg_digambarnya}")
    axnya.set_ylabel(yg_digambarnya)
    axnya.legend(loc="upper right", fontsize=8)



#========================== perkara settings sidebar==========================
st.sidebar.title("🔧 Dashboard Settings")



#----------- checkbox polutan
st.sidebar.subheader("POLLUTANTS")

polutan_checkbox_states = {}
for tiap_polutan in key_polutan_data:
    col1, col2 = st.sidebar.columns([0.7, 0.3])  

    with col1:
        checked = st.checkbox(tiap_polutan, value=True, key=f"st_{tiap_polutan}")
    with col2:
        if checked:
            temp_warna= pollutant_color_map[tiap_polutan]
        else:
            temp_warna= "#D3D3D3"
        
        
        st.markdown(f"<div style='width: 40px; height: 20px; background-color:{temp_warna}; border-radius:3px'></div>", unsafe_allow_html=True)

    polutan_checkbox_states[tiap_polutan] = checked  

selected_polutant = [pollutant for pollutant, checked in polutan_checkbox_states.items() if checked]
st.sidebar.write(f"polutan yg kepilih: {', '.join(selected_polutant)}")

''
''

#----------- checkbox polutan


#============================== perkara tabs per polutan ==========================
# Add some spacing
''
''

tabs = st.tabs(selected_polutant)

for tab, tiap_polutan in zip(tabs, selected_polutant):
    with tab:
        st.subheader(f"dataviz jumlah hari taat AQG untuk {tiap_polutan}")

        temp_polutannya = semuaan_stackedbarchart[tiap_polutan]
        temp_fignya, temp_axnya = stacked_bar_chart_urut(
            polutannya=tiap_polutan,
            datanya=temp_polutannya,
            standar_binnya=standar_who_ok,
            label_binnya=bin_labels,
            palet_warnanya=palet_jojo
        )
        st.pyplot(temp_fignya)
        st.dataframe(temp_polutannya.head())

        heatmaps_ditampilin = f"mo_pamer_dataviz/4_heatmap_tiap_statiun_yg_polutannya_{tiap_polutan}.png"
        st.image(heatmaps_ditampilin)

        
     
    


    
    


 
