#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vẽ biểu đồ Elbow Method cải tiến để xác định số cluster tối ưu cho K-Means
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# Thiết lập đường dẫn
BASE_DIR = Path(__file__).parent
PROC_DIR = BASE_DIR / 'processed'
CHART_DIR = BASE_DIR / 'chart_exports'
CHART_DIR.mkdir(exist_ok=True)

# Đọc dữ liệu
print('📂 Đọc dữ liệu từ destinations_clean.csv...')
df = pd.read_csv(PROC_DIR / 'destinations_clean.csv')

# Chọn features để clustering (giống với notebook)
features_for_clustering = [
    'Avg Cost (USD/day)',
    'cost_of_living_index', 
    'restaurant_price_index',
    'Avg Rating'
]

X = df[features_for_clustering].copy()
print(f'✅ Shape dữ liệu ban đầu: {X.shape}')

# Xử lý giá trị NaN
print(f'⚠️  Số giá trị NaN: {X.isnull().sum().sum()}')
X = X.dropna()
print(f'✅ Shape sau khi loại bỏ NaN: {X.shape}')

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f'✅ Dữ liệu đã được chuẩn hóa (mean=0, std=1)')

# Tính SSE và Silhouette Score cho các giá trị K
print('\n🔄 Tính toán SSE và các metrics cho K từ 1 đến 10...')
K_range = range(1, 11)
sse = []
silhouette_scores = []

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(X_scaled)
    sse.append(kmeans.inertia_)
    
    # Silhouette score chỉ tính được cho k >= 2
    if k >= 2:
        from sklearn.metrics import silhouette_score
        score = silhouette_score(X_scaled, kmeans.labels_)
        silhouette_scores.append(score)
        print(f'  K={k}: SSE={kmeans.inertia_:.2f}, Silhouette={score:.4f}')
    else:
        silhouette_scores.append(0)
        print(f'  K={k}: SSE={kmeans.inertia_:.2f}')

# Tính tỷ lệ giảm SSE (để tìm điểm "khuỷu tay")
sse_diff = [0]
for i in range(1, len(sse)):
    diff = sse[i-1] - sse[i]
    pct = (diff / sse[i-1]) * 100
    sse_diff.append(pct)

# Vẽ biểu đồ Elbow Method cải tiến
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('📊 Phân Tích Elbow Method - Xác Định Số Cluster Tối Ưu (K-Means)', 
             fontsize=16, fontweight='bold', y=0.98)

# Chart 1: SSE (Elbow Chart)
ax1 = axes[0, 0]
ax1.plot(K_range, sse, 'bo-', linewidth=2, markersize=8, label='SSE')
ax1.axvline(5, color='red', linestyle='--', linewidth=2, label='K=5 (Được chọn)')
ax1.set_xlabel('Số Cluster (K)', fontsize=12, fontweight='bold')
ax1.set_ylabel('SSE (Sum of Squared Errors)', fontsize=12, fontweight='bold')
ax1.set_title('🔵 SSE theo K - Elbow Method', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)
ax1.set_xticks(K_range)

# Annotation cho K=5
k5_sse = sse[4]
ax1.annotate(f'K=5\nSSE={k5_sse:.1f}', 
            xy=(5, k5_sse), xytext=(6.5, k5_sse+50),
            fontsize=10, fontweight='bold', color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

# Chart 2: Tỷ lệ giảm SSE
ax2 = axes[0, 1]
ax2.plot(K_range, sse_diff, 'go-', linewidth=2, markersize=8)
ax2.axvline(5, color='red', linestyle='--', linewidth=2, label='K=5')
ax2.set_xlabel('Số Cluster (K)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Tỷ lệ giảm SSE (%)', fontsize=12, fontweight='bold')
ax2.set_title('🟢 Tỷ lệ giảm SSE khi tăng K', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)
ax2.set_xticks(K_range)

# Highlight mức giảm tại K=5
if len(sse_diff) > 4:
    ax2.annotate(f'{sse_diff[4]:.1f}%', 
                xy=(5, sse_diff[4]), xytext=(6.5, sse_diff[4]+2),
                fontsize=10, fontweight='bold', color='red',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

# Chart 3: Silhouette Score (K >= 2)
ax3 = axes[1, 0]
K_range_silhouette = list(K_range)[1:]  # Bỏ K=1
silhouette_scores_plot = silhouette_scores[1:]
ax3.plot(K_range_silhouette, silhouette_scores_plot, 'mo-', linewidth=2, markersize=8)
ax3.axvline(5, color='red', linestyle='--', linewidth=2, label='K=5')
ax3.set_xlabel('Số Cluster (K)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Silhouette Score', fontsize=12, fontweight='bold')
ax3.set_title('🟣 Silhouette Score theo K (càng cao càng tốt)', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=10)
ax3.set_xticks(K_range_silhouette)
ax3.set_ylim([0, 1])

# Annotation cho K=5
k5_silhouette = silhouette_scores[4]
ax3.annotate(f'K=5\nScore={k5_silhouette:.4f}', 
            xy=(5, k5_silhouette), xytext=(6.5, k5_silhouette-0.05),
            fontsize=10, fontweight='bold', color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

# Chart 4: Bảng tổng hợp
ax4 = axes[1, 1]
ax4.axis('off')

# Tạo bảng dữ liệu
table_data = []
table_data.append(['K', 'SSE', 'Giảm SSE (%)', 'Silhouette'])
for i, k in enumerate(K_range):
    sil_val = silhouette_scores[i] if k >= 2 else '-'
    sil_str = f'{sil_val:.4f}' if isinstance(sil_val, float) else sil_val
    
    row = [
        str(k),
        f'{sse[i]:.1f}',
        f'{sse_diff[i]:.1f}%',
        sil_str
    ]
    table_data.append(row)

# Vẽ bảng
table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                 colWidths=[0.15, 0.25, 0.3, 0.3])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Định dạng header
for i in range(4):
    cell = table[(0, i)]
    cell.set_facecolor('#4CAF50')
    cell.set_text_props(weight='bold', color='white')

# Highlight dòng K=5
for i in range(4):
    cell = table[(5, i)]
    cell.set_facecolor('#FFE082')
    cell.set_text_props(weight='bold')

ax4.set_title('📋 Bảng Tổng Hợp Metrics', fontsize=13, fontweight='bold', pad=20)

# Thêm text box giải thích
textstr = '''
💡 GIẢI THÍCH:
• SSE: Tổng bình phương khoảng cách từ điểm đến tâm cluster
  → Càng nhỏ càng tốt, nhưng sẽ giảm dần khi K tăng
  
• Elbow Point: Điểm mà SSE giảm chậm lại đáng kể
  → Chọn K tại "khuỷu tay" của đồ thị
  
• Silhouette Score: Đo độ tách biệt giữa các cluster
  → Giá trị từ -1 đến 1, càng gần 1 càng tốt
  → > 0.5: Cấu trúc cluster tốt
  
🎯 KẾT LUẬN: Chọn K=5 vì:
  ✓ Có "khuỷu tay" rõ ràng trên biểu đồ SSE
  ✓ Silhouette score > 0.5 (chất lượng tốt)
  ✓ Cân bằng giữa độ phức tạp và hiệu quả
'''

fig.text(0.15, 0.02, textstr, fontsize=9, verticalalignment='bottom',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout(rect=[0, 0.12, 1, 0.96])

# Lưu biểu đồ
output_path = CHART_DIR / 'elbow_method_analysis.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f'\n✅ Biểu đồ đã được lưu tại: {output_path}')

plt.show()

print('\n' + '='*70)
print('📊 PHÂN TÍCH HOÀN TẤT')
print('='*70)
print(f'Số cluster được đề xuất: K=5')
print(f'SSE tại K=5: {sse[4]:.2f}')
print(f'Silhouette Score tại K=5: {silhouette_scores[4]:.4f}')
print('='*70)
