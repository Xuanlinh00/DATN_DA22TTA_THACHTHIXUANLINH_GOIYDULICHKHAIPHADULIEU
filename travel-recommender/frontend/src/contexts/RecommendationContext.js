import React, { createContext, useContext, useState, useCallback } from 'react';

const RecommendationContext = createContext(null);

export function RecommendationProvider({ children }) {
  const [recommendationData, setRecommendationData] = useState({
    criteria: null,     // { season, category, budget }
    results: [],        // Danh sách điểm đến đã gợi ý
    matchedRules: [],   // Luật Apriori đã khớp
  });

  const updateRecommendation = useCallback((criteria, results, matchedRules) => {
    setRecommendationData({ criteria, results, matchedRules });
  }, []);

  const clearRecommendation = useCallback(() => {
    setRecommendationData({ criteria: null, results: [], matchedRules: [] });
  }, []);

  return (
    <RecommendationContext.Provider value={{
      ...recommendationData,
      updateRecommendation,
      clearRecommendation,
    }}>
      {children}
    </RecommendationContext.Provider>
  );
}

export function useRecommendation() {
  const context = useContext(RecommendationContext);
  if (!context) {
    throw new Error('useRecommendation must be used within a RecommendationProvider');
  }
  return context;
}

export default RecommendationContext;
