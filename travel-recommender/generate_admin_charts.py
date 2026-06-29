"""
Script để generate code cho các biểu đồ mới trong Admin Page
"""

# Countries Pie Chart Component
countries_chart = """
{/* Countries Distribution Pie Chart */}
{(() => {
  // Get destination data and count by country
  const countryStats = {};
  (modalData.filter(d => d.Country) || []).forEach(d => {
    const country = d.Country;
    countryStats[country] = (countryStats[country] || 0) + 1;
  });
  
  const topCountries = Object.entries(countryStats)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);
  
  const total = topCountries.reduce((sum, [_, count]) => sum + count, 0);
  
  // Pink color palette
  const colors = [
    '#c24482', '#e91e63', '#f06292', '#f48fb1',
    '#fd662f', '#ff9472', '#ffa28a', '#ffc1a2',
    '#f4a4c6', '#fce4ec'
  ];
  
  let currentAngle = 0;
  
  return (
    <>
      <svg viewBox="0 0 200 200" className="pie-chart-svg">
        {topCountries.map(([country, count], idx) => {
          const percentage = count / total;
          const angle = percentage * 360;
          const x1 = 100 + 80 * Math.cos((currentAngle - 90) * Math.PI / 180);
          const y1 = 100 + 80 * Math.sin((currentAngle - 90) * Math.PI / 180);
          currentAngle += angle;
          const x2 = 100 + 80 * Math.cos((currentAngle - 90) * Math.PI / 180);
          const y2 = 100 + 80 * Math.sin((currentAngle - 90) * Math.PI / 180);
          const largeArc = angle > 180 ? 1 : 0;
          
          const path = `M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`;
          
          return (
            <path 
              key={country}
              d={path}
              fill={colors[idx % colors.length]}
              stroke="white"
              strokeWidth="2"
            />
          );
        })}
        <circle cx="100" cy="100" r="40" fill="white" />
        <text x="100" y="95" textAnchor="middle" fontSize="20" fontWeight="bold" fill="#c24482">
          {total}
        </text>
        <text x="100" y="112" textAnchor="middle" fontSize="10" fill="#666">
          Điểm đến
        </text>
      </svg>
      
      <div className="pie-chart-legend">
        {topCountries.map(([country, count], idx) => (
          <div key={country} className="legend-item">
            <span className="legend-color" style={{ backgroundColor: colors[idx % colors.length] }}></span>
            <span className="legend-label">{country}</span>
            <span className="legend-value">{count}</span>
          </div>
        ))}
      </div>
    </>
  );
})()}
"""

# Rules Confidence Chart
rules_chart = """
{/* Top Rules by Confidence */}
{(() => {
  const topRules = (modalData || [])
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 10);
  
  const maxConfidence = topRules[0]?.confidence || 1;
  
  return topRules.map((rule, idx) => {
    const percentage = (rule.confidence / maxConfidence) * 100;
    return (
      <div key={idx} className="rule-bar-item">
        <div className="rule-bar-header">
          <span className="rule-rank">#{idx + 1}</span>
          <span className="rule-confidence">{(rule.confidence * 100).toFixed(1)}%</span>
        </div>
        <div className="rule-bar-container">
          <div 
            className="rule-bar-fill"
            style={{ 
              width: `${percentage}%`,
              background: `linear-gradient(90deg, #c24482, #f4a4c6)`
            }}
          >
            <span className="rule-bar-text">
              Lift: {rule.lift?.toFixed(2)}
            </span>
          </div>
        </div>
        <div className="rule-description" title={rule.rule}>
          {rule.rule.length > 60 ? rule.rule.substring(0, 60) + '...' : rule.rule}
        </div>
      </div>
    );
  });
})()}
"""

print("=" * 60)
print("COUNTRIES PIE CHART COMPONENT")
print("=" * 60)
print(countries_chart)
print("\n" + "=" * 60)
print("RULES CONFIDENCE CHART COMPONENT")
print("=" * 60)
print(rules_chart)
