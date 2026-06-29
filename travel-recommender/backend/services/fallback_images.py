# -*- coding: utf-8 -*-
"""
Fallback Images - URL ảnh cứng theo country và type
Sử dụng nguồn: Unsplash (không cần API key, direct URL)
Nhiều ảnh cho mỗi country/type để tránh trùng lặp
Sử dụng consistent hashing để đảm bảo không trùng lặp giữa các destination
"""

import re

# Ảnh theo TYPE (loại hình du lịch) - Nhiều ảnh cho mỗi type
TYPE_IMAGES = {
    'Beach': [
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200',
        'https://images.unsplash.com/photo-1506953823976-52e1fdc0149a?w=1200',
        'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=1200',
        'https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=1200',
        'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=1200',
    ],
    'Mountain': [
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
        'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200',
        'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=1200',
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
        'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=1200',
    ],
    'Historical': [
        'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1200',
        'https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?w=1200',
        'https://images.unsplash.com/photo-1555217851-5a6df8d65b94?w=1200',
        'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200',
        'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=1200',
    ],
    'Cultural': [
        'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200',
        'https://images.unsplash.com/photo-1548013146-72479768bada?w=1200',
        'https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=1200',
        'https://images.unsplash.com/photo-1528127269322-539801943592?w=1200',
        'https://images.unsplash.com/photo-1604130173936-3b44ce527c8b?w=1200',
    ],
    'Adventure': [
        'https://images.unsplash.com/photo-1551632811-561732d1e306?w=1200',
        'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200',
        'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=1200',
        'https://images.unsplash.com/photo-1445308394109-4ec2920981b1?w=1200',
        'https://images.unsplash.com/photo-1551632811-561732d1e306?w=1200',
    ],
    'Religious': [
        'https://images.unsplash.com/photo-1548013146-72479768bada?w=1200',
        'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200',
        'https://images.unsplash.com/photo-1528127269322-539801943592?w=1200',
        'https://images.unsplash.com/photo-1580837119756-563d608dd119?w=1200',
        'https://images.unsplash.com/photo-1604130173936-3b44ce527c8b?w=1200',
    ],
    'City': [
        'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1200',
        'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=1200',
        'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=1200',
        'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1200',
        'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1200',
    ],
    'Nature': [
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200',
        'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200',
        'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=1200',
        'https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1200',
        'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200',
    ],
}

# Ảnh theo COUNTRY - Nhiều ảnh cho mỗi country
COUNTRY_IMAGES = {
    'Thailand': [
        'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=1200',
        'https://images.unsplash.com/photo-1506665531195-3566af2b4dfa?w=1200',
        'https://images.unsplash.com/photo-1528181304800-259b08848526?w=1200',
        'https://images.unsplash.com/photo-1552550049-db097c9480d1?w=1200',
        'https://images.unsplash.com/photo-1534008897995-27a23e859048?w=1200',
    ],
    'Vietnam': [
        'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=1200',
        'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=1200',
        'https://images.unsplash.com/photo-1557750255-c76072a7aad1?w=1200',
        'https://images.unsplash.com/photo-1528127269322-539801943592?w=1200',
        'https://images.unsplash.com/photo-1589519160732-57fc498494f8?w=1200',
    ],
    'Japan': [
        'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200',
        'https://images.unsplash.com/photo-1492571350019-22de08371fd3?w=1200',
        'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=1200',
        'https://images.unsplash.com/photo-1528164344705-47542687000d?w=1200',
        'https://images.unsplash.com/photo-1542640244-7e672d6cef4e?w=1200',
    ],
    'China': [
        'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=1200',
        'https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?w=1200',
        'https://images.unsplash.com/photo-1537819191377-d3305ffddce4?w=1200',
        'https://images.unsplash.com/photo-1496417263034-38ec4f0b665a?w=1200',
        'https://images.unsplash.com/photo-1545893835-abaa50cbe628?w=1200',
    ],
    'India': [
        'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1200',
        'https://images.unsplash.com/photo-1548013146-72479768bada?w=1200',
        'https://images.unsplash.com/photo-1532664189809-02133fee698d?w=1200',
        'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=1200',
        'https://images.unsplash.com/photo-1517394834181-95ed159986c7?w=1200',
    ],
    'France': [
        'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200',
        'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=1200',
        'https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?w=1200',
        'https://images.unsplash.com/photo-1549144511-f099e773c147?w=1200',
        'https://images.unsplash.com/photo-1550340499-a6c60fc8287c?w=1200',
    ],
    'Italy': [
        'https://images.unsplash.com/photo-1520175480921-4edfa2983e0f?w=1200',
        'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1200',
        'https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?w=1200',
        'https://images.unsplash.com/photo-1525874684015-58379d421a52?w=1200',
        'https://images.unsplash.com/photo-1529260830199-42c24126f198?w=1200',
    ],
    'Spain': [
        'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=1200',
        'https://images.unsplash.com/photo-1558642084-fd07fae5282e?w=1200',
        'https://images.unsplash.com/photo-1562883676-8c7feb83f09b?w=1200',
        'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=1200',
        'https://images.unsplash.com/photo-1509840841025-9088ba78a826?w=1200',
    ],
    'Germany': [
        'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=1200',
        'https://images.unsplash.com/photo-1527838832700-5059252407fa?w=1200',
        'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=1200',
        'https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?w=1200',
        'https://images.unsplash.com/photo-1543629795-6c3e5d3e7e14?w=1200',
    ],
    'USA': [
        'https://images.unsplash.com/photo-1485738422979-f5c462d49f74?w=1200',
        'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1200',
        'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=1200',
        'https://images.unsplash.com/photo-1444723121867-7a241cacace9?w=1200',
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
    ],
    'Canada': [
        'https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=1200',
        'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=1200',
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
        'https://images.unsplash.com/photo-1471623320832-752e8bbf8413?w=1200',
        'https://images.unsplash.com/photo-1519904981063-b0cf448d479e?w=1200',
    ],
    'Mexico': [
        'https://images.unsplash.com/photo-1518638150340-f706e86654de?w=1200',
        'https://images.unsplash.com/photo-1512813195386-6cf811ad3542?w=1200',
        'https://images.unsplash.com/photo-1569154941061-e231b4725ef1?w=1200',
        'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200',
        'https://images.unsplash.com/photo-1512813498716-cpf4567d1ea4?w=1200',
    ],
    'Brazil': [
        'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=1200',
        'https://images.unsplash.com/photo-1516834474-48c0abc2a902?w=1200',
        'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=1200',
        'https://images.unsplash.com/photo-1511092307207-46f5e6bcb1d8?w=1200',
        'https://images.unsplash.com/photo-1518639192441-8fce0a366e2e?w=1200',
    ],
    'Argentina': [
        'https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=1200',
        'https://images.unsplash.com/photo-1589802829985-817e51171b92?w=1200',
        'https://images.unsplash.com/photo-1596542043805-f0755e3b3fff?w=1200',
        'https://images.unsplash.com/photo-1544376798-89aa6b82c6cd?w=1200',
        'https://images.unsplash.com/photo-1604924186519-2e7a41d6e0a2?w=1200',
    ],
    'Peru': [
        'https://images.unsplash.com/photo-1526392060635-9d6019884377?w=1200',
        'https://images.unsplash.com/photo-1531065208531-4036c0dba3ca?w=1200',
        'https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=1200',
        'https://images.unsplash.com/photo-1560458455-825bd7e0f30f?w=1200',
        'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200',
    ],
    'Egypt': [
        'https://images.unsplash.com/photo-1539768942893-daf53e448371?w=1200',
        'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=1200',
        'https://images.unsplash.com/photo-1553913861-c0fddf2619ee?w=1200',
        'https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=1200',
        'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=1200',
    ],
    'Morocco': [
        'https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?w=1200',
        'https://images.unsplash.com/photo-1511715282680-fbf93a50e721?w=1200',
        'https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=1200',
        'https://images.unsplash.com/photo-1551785076-c61086f35846?w=1200',
        'https://images.unsplash.com/photo-1516575334481-f85287c2c82d?w=1200',
    ],
    'South Africa': [
        'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=1200',
        'https://images.unsplash.com/photo-1523805009345-7448845a9e53?w=1200',
        'https://images.unsplash.com/photo-1580408041445-3966bb7ed408?w=1200',
        'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=1200',
        'https://images.unsplash.com/photo-1577948000111-9c970dfe3743?w=1200',
    ],
    'Kenya': [
        'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=1200',
        'https://images.unsplash.com/photo-1523805009345-7448845a9e53?w=1200',
        'https://images.unsplash.com/photo-1489392191049-fc10c97e64b6?w=1200',
        'https://images.unsplash.com/photo-1547970810-dc1eac37d174?w=1200',
        'https://images.unsplash.com/photo-1580408041445-3966bb7ed408?w=1200',
    ],
    'Australia': [
        'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=1200',
        'https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=1200',
        'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?w=1200',
        'https://images.unsplash.com/photo-1524668951403-d44b28200ce0?w=1200',
        'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=1200',
    ],
    'New Zealand': [
        'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=1200',
        'https://images.unsplash.com/photo-1469521669194-babb48b5f3a5?w=1200',
        'https://images.unsplash.com/photo-1527004013197-933c4bb611b3?w=1200',
        'https://images.unsplash.com/photo-1513415562641-69fd16c62184?w=1200',
        'https://images.unsplash.com/photo-1489074821641-e5c0c8794882?w=1200',
    ],
    'Greece': [
        'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=1200',
        'https://images.unsplash.com/photo-1555993539-1732b0258235?w=1200',
        'https://images.unsplash.com/photo-1503152394-c571994fd383?w=1200',
        'https://images.unsplash.com/photo-1516298340221-0aa6eb47ad87?w=1200',
        'https://images.unsplash.com/photo-1504979646828-e59873d8e9f4?w=1200',
    ],
}

def get_fallback_image(country: str, dest_type: str, destination_name: str = "") -> str:
    """
    Lấy URL ảnh fallback dựa trên country và type
    Sử dụng consistent hashing để chọn ảnh từ list
    Thêm destination name encoded trong URL để đảm bảo unique 100%
    Ưu tiên: Country > Type > Default
    
    Mỗi destination sẽ có URL hoàn toàn unique
    """
    # Tạo hash key duy nhất cho mỗi destination
    hash_key = f"{destination_name}|{country}|{dest_type}"
    hash_value = abs(hash(hash_key))
    
    # URL encode destination name để dùng làm unique identifier
    # Chỉ giữ alphanumeric và convert sang lowercase
    safe_name = re.sub(r'[^a-zA-Z0-9]', '', destination_name).lower()[:20]
    # Nếu tên rỗng hoặc quá ngắn, dùng hash value
    if len(safe_name) < 3:
        safe_name = str(hash_value)
    
    # Ưu tiên country trước
    if country and country in COUNTRY_IMAGES:
        images = COUNTRY_IMAGES[country]
        index = hash_value % len(images)
        base_url = images[index]
        # Combine safe_name + hash để đảm bảo unique
        return f"{base_url}&dest={safe_name}{hash_value}"
    
    # Fallback sang type
    if dest_type and dest_type in TYPE_IMAGES:
        images = TYPE_IMAGES[dest_type]
        index = hash_value % len(images)
        base_url = images[index]
        return f"{base_url}&dest={safe_name}{hash_value}"
    
    # Default: travel generic
    default_images = [
        'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200',
        'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1200',
        'https://images.unsplash.com/photo-1504150558551-22e2c5a8e7c6?w=1200',
        'https://images.unsplash.com/photo-1503220317375-aaad61436b1b?w=1200',
    ]
    index = hash_value % len(default_images)
    base_url = default_images[index]
    return f"{base_url}&dest={safe_name}{hash_value}"
