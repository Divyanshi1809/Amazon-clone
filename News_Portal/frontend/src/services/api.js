import axios from "axios";

const API_BASE_URL='http://localhost:5000/api';

const api=axios.create({
    baseURL :API_BASE_URL,
    headers: {
        'Content-Type':'application/json',
    },
});

api.interceptors.request.use(
    (config) => {
        const token=localStorage.getItem('token');
        if(token){
            config.headers.Authorization=`Bearer ${token}`;

        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if(error.response?.status===401){
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href='/login';
        }
        return Promise.reject(error);
    }
);


export const authAPI={
    login : async (credentials) =>{
        const response=await api.post('/auth/login',credentials);
        return response.data;
    },
    register: async (credentials) =>{
        const response=await api.post('/auth/register',credentials);
        return response.data;
    },
    logout: ()=>{
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },
};
export const newsAPI = {
    getNews: async (params = {}) => {
      const response = await api.get('/news', { params });
      return response.data;
    },
    
    getNewsById: async (id) => {
      const response = await api.get(`/news/${id}`);
      return response.data;
    },
    
    searchNews: async (query, params = {}) => {
      const response = await api.get('/news/search', {
        params: { q: query, ...params }
      });
      return response.data;
    },
    
    getCategories: async () => {
      const response = await api.get('/news/categories');
      return response.data;
    },
    
    getSources: async () => {
      const response = await api.get('/news/sources');
      return response.data;
    },
    
    getRecommendations: async (params = {}) => {
      const response = await api.get('/news/recommendations', { params });
      return response.data;
    },
    
    predictFakeNews: async (article) => {
      const response = await api.post('/news/fake-news/predict', { article });
      return response.data;
    },
    
    analyzeSentiment: async (text) => {
      const response = await api.post('/news/analyze-sentiment', { text });
      return response.data;
    },
    
    getTrendingTopics: async (days = 7, limit = 10) => {
      const response = await api.get('/news/trending', {
        params: { days, limit }
      });
      return response.data;
    },
    
    getNewsBySentiment: async (sentiment, category = 'general') => {
      const response = await api.get(`/news/sentiment/${sentiment}`, {
        params: { category }
      });
      return response.data;
    },
    
    triggerScraping: async (categories = null) => {
      const response = await api.post('/news/scrape', { categories });
      return response.data;
    },
};

// Bookmarks API calls
export const bookmarksAPI = {
  getBookmarks: async () => {
    const response = await api.get('/bookmarks');
    return response.data;
  },
  
  addBookmark: async (bookmarkData) => {
    const response = await api.post('/bookmarks', bookmarkData);
    return response.data;
  },
  
  removeBookmark: async (newsId) => {
    const response = await api.delete(`/bookmarks/${newsId}`);
    return response.data;
  },
  
  isBookmarked: async (newsId) => {
    const response = await api.get(`/bookmarks/check/${newsId}`);
    return response.data;
  },
};


// Analytics API calls
export const analyticsAPI = {
  getUserAnalytics: async (days = 30) => {
    const response = await api.get('/analytics/user', { params: { days } });
    return response.data;
  },
  
  getDashboard: async (days = 30) => {
    const response = await api.get('/analytics/dashboard', { params: { days } });
    return response.data;
  },
  
  getTrending: async (days = 7, limit = 10) => {
    const response = await api.get('/analytics/trending', {
      params: { days, limit }
    });
    return response.data;
  },
  
  getSentimentAnalysis: async (days = 7) => {
    const response = await api.get('/analytics/sentiment', { params: { days } });
    return response.data;
  },
  
  getFakeNewsStats: async (days = 30) => {
    const response = await api.get('/analytics/fake-news-stats', { params: { days } });
    return response.data;
  },
  
  getCTR: async (days = 30) => {
    const response = await api.get('/analytics/ctr', { params: { days } });
    return response.data;
  },
};

// User Interaction API
export const interactionAPI = {
  trackInteraction: async (newsId, interactionType, category = null) => {
    const response = await api.post('/interactions', {
      news_id: newsId,
      interaction_type: interactionType,
      category
    });
    return response.data;
  },
  
  trackReadingTime: async (newsId, timeSpentSeconds, category = null, completed = false) => {
    const response = await api.post('/reading-history', {
      news_id: newsId,
      time_spent_seconds: timeSpentSeconds,
      category,
      completed
    });
    return response.data;
  },
};

export const getAuthToken = () => localStorage.getItem('token');
export const getUser = () => JSON.parse(localStorage.getItem('user') || 'null');
export const isAuthenticated = () => !!getAuthToken();

export default api;