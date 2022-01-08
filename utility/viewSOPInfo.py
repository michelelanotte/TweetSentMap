class ViewSOPInfo:
    def __init__(self):
        self.__cities = ["wellington", "san francisco", "new york", "sydney", "london"]
        self.__dataset = None
        self.__df_selected_city = None
        
        #Dictionary which will contain the midpoints of the cities indicate as keys.
        #the elements will be in the form: <lat, lon>
        self.__dict_coords_midpoint = None
        
        #Dictionary which will contain the bbox of the cities indicate as keys
        #the elements will be in the form: <<lat_min, lat_max>, <lon_min, lon_max>>
        self.__dict_coords_bbox = None
        self.__fig_map = None
        self.__fig_pie = None
        self.__fig_selected_area = None
        self.__title = ""
        
    def set_dataset(self, dataset):
            self.__dataset = dataset
    
    def get_dataset(self):
            return self.__dataset
    
    def set_df_selected_city(self, df):
            self.__df_selected_city = df
    
    def get_df_selected_city(self):
            return self.__df_selected_city

    def set_dict_coords_midpoint(self, dict_coords_midpoint):
            self.__dict_coords_midpoint = dict_coords_midpoint
    
    def get_dict_coords_midpoint(self):
            return self.__dict_coords_midpoint

    def set_dict_coords_bbox(self, dict_coords_bbox):
            self.__dict_coords_bbox = dict_coords_bbox
    
    def get_dict_coords_bbox(self):
            return self.__dict_coords_bbox
    
    def set_fig_map(self, fig_map):
        self.__fig_map = fig_map
    
    def get_fig_map(self):
        return self.__fig_map
    
    def set_fig_pie(self, fig_pie):
        self.__fig_pie = fig_pie
    
    def get_fig_pie(self):
        return self.__fig_pie
    
    def set_fig_selected_area(self, fig_selected_area):
        self.__fig_selected_area = fig_selected_area
    
    def get_fig_selected_area(self):
        return self.__fig_selected_area

    def set_title(self, title):
        self.__title = title
          
    def get_title(self):
        return self.__title
    
    def get_cities(self):
        return self.__cities
    
    def get_city_by_index(self, i):
        return self.__cities[i]
        