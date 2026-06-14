// -*- coding: utf-8 -*-
/**
 * Image Service - Tự động gán hình ảnh du lịch cho từng địa điểm.
 *
 * Ưu tiên theo thứ tự:
 *   1. EXACT_DESTINATION_IMAGES – hình ảnh đã kiểm duyệt thủ công cho từng địa điểm cụ thể
 *   2. COUNTRY_TYPE_IMAGES – hình theo quốc gia + loại du lịch (cho các tên generic)
 *   3. IMAGES_BY_TYPE – hình ảnh chung theo loại (fallback cuối cùng)
 */

// ── CURATED IMAGES: Hình ảnh chung theo loại du lịch ──────────────────────────
const IMAGES_BY_TYPE = {
  waterfall: [
    'https://images.unsplash.com/photo-1558431382-27e303142255?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1504829857797-ddff29c27927?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1667420170858-39d40cb413e3?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1585219581414-4442041c2d03?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1593322962878-a4b73deb1e39?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1465188162913-8fb5709d6d57?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1432405972618-c6b0cfba8673?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1540206395-68808572332f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1567850051328-77f4b1a6d5c8?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1546587348-d12660c30c50?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1562679299-31a47f9f49a5?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1520962880247-cfaf541c8724?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1495475689903-93708929d8c7?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1424581342241-47e9a0a4a460?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1543731068-7e0f5beff43a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1517439270744-ba4a43d2dfce?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1503435980610-a51f3ddfee50?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1433838552652-f9a46b332c40?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1565638459249-c85cbb30e72e?w=600&auto=format&fit=crop&q=60'
  ],
  beach: [
    'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1473116763269-255ea760754e?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1520116468888-95b2d18a79b2?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1515238152791-8216bfdf89a7?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1520942702018-0862200e6873?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1468413253725-0d5181026218?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1509233725247-49e657c54213?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1540979388789-6cee28a1cdc9?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1484821582734-6c6c9a0e3e13?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1530053969600-caed2596d242?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1494094892896-7f14a4433b7a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1506953823976-52e1fdc0149a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1507876466758-bc54f384809c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1559628233-100c798642d4?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1537956965359-7573183d1f57?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1471922694854-ff1b63b20054?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1535916707507-35f07e601631?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&auto=format&fit=crop&q=60'
  ],
  mountain: [
    'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1486873249359-2731bd6dafc7?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1492641164460-e2d33b4e3412?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1482862549707-f63cb32c5fd9?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1416339306562-f3d12fefd36f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1549880338-65ddcdfd017b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1463693396721-8ca0cfa373b4?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1477346611705-65d1883cee1e?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1516302752625-fcc3c50ae61f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1527668752968-14dc70a27c95?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1508873696983-2dfd5898f08b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1580655653885-65763b2597d0?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1531794590132-5c04be1a0972?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1502784444187-359ac186c5bb?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1526392060635-9d6019884377?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1518022525094-e099d3adb126?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1549421263-6e398d5c4146?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1540611025311-01df3cef54b5?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1501179691627-eeaa65ea017c?w=600&auto=format&fit=crop&q=60'
  ],
  cultural: [
    'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1449034446853-66c86144b0ad?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1518638150341-db700683457a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1524413840003-05174b1e7d48?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1503152394-c571994fd383?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1528127269322-539801943592?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1564507592937-25994a9015b2?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1471306224500-6d0d218be372?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1569700679541-2e70dcc19800?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1538485399081-7191377e8241?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1583417267826-aebc4d1542e1?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1538076761142-07c47c1d1b5a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1586613835341-e0ce4f711e2a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1558799401-1dcdef79d949?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1562154926-190a02f1a96c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1541849546-216549ae216d?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1559113202-c916b8e44373?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1539768942893-daf53e736b68?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1585208798174-6cedd86e019a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1575001560614-e68012d0949a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1555990538-1d3c0e30e55c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1549918864-48ac978761a4?w=600&auto=format&fit=crop&q=60'
  ],
  nature: [
    'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1472214222541-d510753a4907?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1500627869374-13cd993b1115?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1433832597046-4f10e10ac764?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1518173946687-a4c8a383392f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1511497584788-876760111969?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1421919514768-689368d43d1a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1504945005722-33670dcaf685?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1519611103964-90f61a44f486?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1547036980-1095cf077e20?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1570789210967-2cac24ee872d?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1580191947416-62d35a55e71d?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1590098563414-82b19b37cc05?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1548777123-e216912df7d8?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1476610182048-b716b8515aaa?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1534445867742-43195f401b6c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1513415277900-a62401e19be4?w=600&auto=format&fit=crop&q=60'
  ],
  adventure: [
    'https://images.unsplash.com/photo-1501555088652-021faa106b9b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1527853787696-f7bc74c2e357?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1533240332313-0db49b459ad6?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1483168527879-c66136b56105?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1521336575822-6da63fb4af4c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1530866495561-507c9faab2ed?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1520769669658-f07657f5a307?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1565967511849-76a60a516170?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1547483238-2cbf881a559f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1548571364-cee53ee7ea7a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1621414050946-1b936a78cf55?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1524337676612-18a37daa4e63?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1600078686889-8c2d32f9a008?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1515224526905-51c7d77c7057?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1531168556467-80aace0d0144?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600&auto=format&fit=crop&q=60'
  ],
  urban: [
    'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1496568818309-53d7c7753022?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1490642914619-7955a3fd483c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1449034446853-66c86144b0ad?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1475855581690-80accde3ae2b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1538538928580-eb46f5dda73d?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1543508282-6319a3e2621f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1470004914212-05527e49370b?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1509356843151-3e7d96241e11?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1513622470522-26c3c8a854bc?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1551867633-194f125bddfa?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1560184611-ff3e53f00e13?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1559107180-c30f1e5b1d10?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1582672060674-bc2bd808a8b5?w=600&auto=format&fit=crop&q=60'
  ],
  default: [
    'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1533104816931-20fa691ff6ca?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1547483238-2cbf881a559f?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1520769669658-f07657f5a307?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1501179691627-eeaa65ea017c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1559628233-100c798642d4?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1534445867742-43195f401b6c?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=600&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=600&auto=format&fit=crop&q=60'
  ]
};

// ── EXACT IMAGES: Hình ảnh đã kiểm duyệt cho từng địa điểm cụ thể ────────
export const EXACT_DESTINATION_IMAGES = {
  // ─── Châu Á ───────────────────────────────────────────
  'Seoul Tower & Palace': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Front_view_of_the_tower_of_Jibokjae_Hall_under_blue_sky_at_Gyeongbokgung_Palace_in_Seoul.jpg/1280px-Front_view_of_the_tower_of_Jibokjae_Hall_under_blue_sky_at_Gyeongbokgung_Palace_in_Seoul.jpg',
  'Marina Bay Sands & Gardens': 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&auto=format&fit=crop&q=80',
  'Maldives Overwater Villas': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&auto=format&fit=crop&q=80',
  'Taj Mahal': 'https://images.unsplash.com/photo-1564507592937-25994a9015b2?w=800&auto=format&fit=crop&q=80',
  'Leh Ladakh': 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?w=800&auto=format&fit=crop&q=80',
  'Jaipur City': 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&auto=format&fit=crop&q=80',
  'Kerala Backwaters': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&auto=format&fit=crop&q=80',
  'Goa Beaches': 'https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=800&auto=format&fit=crop&q=80',
  'Seoul Tower & Palace': 'https://images.unsplash.com/photo-1538485399081-7191377e8241?w=800&auto=format&fit=crop&q=80',
  'Jeju Island Beaches': 'https://images.unsplash.com/photo-1579169326371-e7c429da59e0?w=800&auto=format&fit=crop&q=80',
  'Sentosa Island Resort': 'https://images.unsplash.com/photo-1565967511849-76a60a516170?w=800&auto=format&fit=crop&q=80',
  'Ubud Bali Cultural Tour': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&auto=format&fit=crop&q=80',
  'Phuket Patong Beach Party': 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=800&auto=format&fit=crop&q=80',
  'Chiang Mai Lantern Festival': 'https://images.unsplash.com/photo-1504214208698-ea1916a2195a?w=800&auto=format&fit=crop&q=80',
  'Kyoto Fushimi Inari Shrine': 'https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=800&auto=format&fit=crop&q=80',
  'Osaka Dotonbori Street Food': 'https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800&auto=format&fit=crop&q=80',
  'Shanghai The Bund Skyline': 'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=800&auto=format&fit=crop&q=80',
  'Great Wall of China': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&auto=format&fit=crop&q=80',
  'Zhangjiajie Avatar Mountains': 'https://images.unsplash.com/photo-1513415277900-a62401e19be4?w=800&auto=format&fit=crop&q=80',
  'Kuala Lumpur Petronas Towers': 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&auto=format&fit=crop&q=80',
  'Langkawi Cable Car & SkyBridge': 'https://images.unsplash.com/photo-1596803244618-8dbee61a3e52?w=800&auto=format&fit=crop&q=80',
  'Penang Georgetown Heritage Art': 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
  'Kota Kinabalu Nature Trekking': 'https://images.unsplash.com/photo-1580655653885-65763b2597d0?w=800&auto=format&fit=crop&q=80',
  'El Nido Bacuit Bay Islands': 'https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=800&auto=format&fit=crop&q=80',
  'Chocolate Hills Bohol Adventure': 'https://images.unsplash.com/photo-1570789210967-2cac24ee872d?w=800&auto=format&fit=crop&q=80',
  'Intramuros Walled City Manila': 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800&auto=format&fit=crop&q=80',
  'Angkor Wat Temples': 'https://images.unsplash.com/photo-1569700679541-2e70dcc19800?w=800&auto=format&fit=crop&q=80',
  'Koh Rong Tropical Beaches': 'https://images.unsplash.com/photo-1559628233-100c798642d4?w=800&auto=format&fit=crop&q=80',
  'Phnom Penh Palace & Silver Pagoda': 'https://images.unsplash.com/photo-1575001560614-e68012d0949a?w=800&auto=format&fit=crop&q=80',
  'Luang Prabang Heritage Town': 'https://images.unsplash.com/photo-1583417267826-aebc4d1542e1?w=800&auto=format&fit=crop&q=80',
  'Kuang Si Turquoise Waterfalls': 'https://images.unsplash.com/photo-1558431382-27e303142255?w=800&auto=format&fit=crop&q=80',
  'Vang Vieng Karst Nature Tour': 'https://images.unsplash.com/photo-1549421263-6e398d5c4146?w=800&auto=format&fit=crop&q=80',
  'Shwedagon Pagoda Yangon': 'https://images.unsplash.com/photo-1538076761142-07c47c1d1b5a?w=800&auto=format&fit=crop&q=80',
  'Inle Lake Fisherman Villages': 'https://images.unsplash.com/photo-1540611025311-01df3cef54b5?w=800&auto=format&fit=crop&q=80',
  'Sigiriya Ancient Lion Rock': 'https://images.unsplash.com/photo-1586613835341-e0ce4f711e2a?w=800&auto=format&fit=crop&q=80',
  'Ella Train & Nine Arch Bridge': 'https://images.unsplash.com/photo-1580191947416-62d35a55e71d?w=800&auto=format&fit=crop&q=80',
  'Temple of the Tooth Kandy': 'https://images.unsplash.com/photo-1588598198321-9735fd52ccef?w=800&auto=format&fit=crop&q=80',
  'Kathmandu Durbar Square Temples': 'https://images.unsplash.com/photo-1558799401-1dcdef79d949?w=800&auto=format&fit=crop&q=80',
  'Everest Base Camp Mountain Trek': 'https://images.unsplash.com/photo-1516302752625-fcc3c50ae61f?w=800&auto=format&fit=crop&q=80',
  'Pokhara Phewa Lake Resort': 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800&auto=format&fit=crop&q=80',
  'Taipei 101 Observatory': 'https://images.unsplash.com/photo-1470004914212-05527e49370b?w=800&auto=format&fit=crop&q=80',
  'Jiufen Old Street Lanterns': 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&auto=format&fit=crop&q=80',
  'Taroko Marble Gorge National Park': 'https://images.unsplash.com/photo-1588997718457-6278d0756dca?w=800&auto=format&fit=crop&q=80',
  'Gobi Desert Singing Dunes': 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&auto=format&fit=crop&q=80',
  'Terelj National Park Ger Camp': 'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=800&auto=format&fit=crop&q=80',
  'Burj Khalifa Dubai': 'https://images.unsplash.com/photo-1582672060674-bc2bd808a8b5?w=800&auto=format&fit=crop&q=80',
  'Maafushi Budget Beaches': 'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=800&auto=format&fit=crop&q=80',
  'Sapa Terrace Rice Fields': 'https://images.unsplash.com/photo-1508873696983-2dfd5898f08b?w=800&auto=format&fit=crop&q=80',
  'Phu Quoc Sunset Beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
  'Trang An Scenic Landscape': 'https://images.unsplash.com/photo-1528127269322-539801943592?w=800&auto=format&fit=crop&q=80',

  // ─── Châu Âu ─────────────────────────────────────────
  'Rotterdam Futuristic Architecture': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/GraphyArchy_-_Wikipedia_00096.jpg/1280px-GraphyArchy_-_Wikipedia_00096.jpg',
  'Ghent Castle of the Counts': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Gent_Gravensteen_R01.jpg/1280px-Gent_Gravensteen_R01.jpg',
  'Kronborg Castle Elsinore': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Kronborg_002.JPG/1280px-Kronborg_002.JPG',
  'Bergen Bryggen Wharf': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Bryggen%2C_Bergen%2C_Noruega%2C_2019-09-08%2C_DD_115-117_PAN.jpg/1280px-Bryggen%2C_Bergen%2C_Noruega%2C_2019-09-08%2C_DD_115-117_PAN.jpg',
  'Zermatt Matterhorn Peak': 'https://images.unsplash.com/photo-1502784444187-359ac186c5bb?w=800&auto=format&fit=crop&q=80',
  'Santorini Island Sunsets': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&auto=format&fit=crop&q=80',
  'Interlaken Adventure': 'https://images.unsplash.com/photo-1527668752968-14dc70a27c95?w=800&auto=format&fit=crop&q=80',
  'Cappadocia Hot Balloons': 'https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?w=800&auto=format&fit=crop&q=80',
  'Istanbul Hagia Sophia': 'https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=800&auto=format&fit=crop&q=80',
  'London Big Ben & Eye': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&auto=format&fit=crop&q=80',
  'Keukenhof Tulip Festival': 'https://images.unsplash.com/photo-1550931454-41e17df20e06?w=800&auto=format&fit=crop&q=80',
  'Amsterdam Historic Canal Cruise': 'https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800&auto=format&fit=crop&q=80',
  'Zaanse Schans Windmill Village': 'https://images.unsplash.com/photo-1512470876337-d64b2680e3a3?w=800&auto=format&fit=crop&q=80',
  'Giethoorn Village Without Roads': 'https://images.unsplash.com/photo-1588392382834-a891154bca4d?w=800&auto=format&fit=crop&q=80',
  'Rotterdam Futuristic Architecture': 'https://images.unsplash.com/photo-1543508282-6319a3e2621f?w=800&auto=format&fit=crop&q=80',
  'Bruges Medieval Canal Tour': 'https://images.unsplash.com/photo-1491557345352-5929e343eb89?w=800&auto=format&fit=crop&q=80',
  'Brussels Grand Place': 'https://images.unsplash.com/photo-1559113202-c916b8e44373?w=800&auto=format&fit=crop&q=80',
  'Ghent Castle of the Counts': 'https://images.unsplash.com/photo-1581870262861-e6e3b2bff3ea?w=800&auto=format&fit=crop&q=80',
  'Hallstatt Alpine Village': 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800&auto=format&fit=crop&q=80',
  'Innsbruck Alpine Skiing': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&auto=format&fit=crop&q=80',
  'Vienna Schonbrunn Palace': 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800&auto=format&fit=crop&q=80',
  'Salzburg Mozart Heritage': 'https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=800&auto=format&fit=crop&q=80',
  'Prague Charles Bridge & Castle': 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&auto=format&fit=crop&q=80',
  'Cesky Krumlov Castle Town': 'https://images.unsplash.com/photo-1560184611-ff3e53f00e13?w=800&auto=format&fit=crop&q=80',
  'Karlovy Vary Spa Town': 'https://images.unsplash.com/photo-1562883676-8c7feb83f09b?w=800&auto=format&fit=crop&q=80',
  'Krakow Wawel Castle & Square': 'https://images.unsplash.com/photo-1562154926-190a02f1a96c?w=800&auto=format&fit=crop&q=80',
  'Warsaw Old Town Restoration': 'https://images.unsplash.com/photo-1524337676612-18a37daa4e63?w=800&auto=format&fit=crop&q=80',
  'Tatra Mountains Zakopane': 'https://images.unsplash.com/photo-1477346611705-65d1883cee1e?w=800&auto=format&fit=crop&q=80',
  'Szechenyi Thermal Bath Pools': 'https://images.unsplash.com/photo-1551867633-194f125bddfa?w=800&auto=format&fit=crop&q=80',
  'Lake Balaton Resort Beaches': 'https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=800&auto=format&fit=crop&q=80',
  'Dubrovnik Game of Thrones Walls': 'https://images.unsplash.com/photo-1555990538-1d3c0e30e55c?w=800&auto=format&fit=crop&q=80',
  'Split Diocletian Palace': 'https://images.unsplash.com/photo-1565620731-169b73643759?w=800&auto=format&fit=crop&q=80',
  'Hvar Island Sun & Yacht Port': 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=800&auto=format&fit=crop&q=80',
  'Plitvice Lakes Waterfall Trail': 'https://images.unsplash.com/photo-1558431382-27e303142255?w=800&auto=format&fit=crop&q=80',
  'Lisbon Alfama & Tram 28': 'https://images.unsplash.com/photo-1585208798174-6cedd86e019a?w=800&auto=format&fit=crop&q=80',
  'Sintra Pena Palace': 'https://images.unsplash.com/photo-1580323956656-26baa985db0f?w=800&auto=format&fit=crop&q=80',
  'Porto Douro Vineyard Valley': 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=800&auto=format&fit=crop&q=80',
  'Dublin Guinness & Trinity College': 'https://images.unsplash.com/photo-1549918864-48ac978761a4?w=800&auto=format&fit=crop&q=80',
  'Cliffs of Moher Coastal Walk': 'https://images.unsplash.com/photo-1548571364-cee53ee7ea7a?w=800&auto=format&fit=crop&q=80',
  'Killarney Ring of Kerry Tour': 'https://images.unsplash.com/photo-1590098563414-82b19b37cc05?w=800&auto=format&fit=crop&q=80',
  'Stockholm Gamla Stan': 'https://images.unsplash.com/photo-1509356843151-3e7d96241e11?w=800&auto=format&fit=crop&q=80',
  'Copenhagen Nyhavn Harbour': 'https://images.unsplash.com/photo-1513622470522-26c3c8a854bc?w=800&auto=format&fit=crop&q=80',
  'Kronborg Castle Elsinore': 'https://images.unsplash.com/photo-1559107180-c30f1e5b1d10?w=800&auto=format&fit=crop&q=80',
  'Tivoli Gardens Theme Park': 'https://images.unsplash.com/photo-1513622470522-26c3c8a854bc?w=800&auto=format&fit=crop&q=80',
  'Helsinki Cathedral & Market': 'https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?w=800&auto=format&fit=crop&q=80',
  'Rovaniemi Santa Claus Village': 'https://images.unsplash.com/photo-1548777123-e216912df7d8?w=800&auto=format&fit=crop&q=80',
  'Finnish Lakeland & Sauna Tour': 'https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?w=800&auto=format&fit=crop&q=80',
  'Reykjavik Blue Lagoon Spa': 'https://images.unsplash.com/photo-1515224526905-51c7d77c7057?w=800&auto=format&fit=crop&q=80',
  'Gullfoss Golden Waterfall': 'https://images.unsplash.com/photo-1504829857797-ddff29c27927?w=800&auto=format&fit=crop&q=80',
  'Jokulsarlon Glacier Lagoon': 'https://images.unsplash.com/photo-1476610182048-b716b8515aaa?w=800&auto=format&fit=crop&q=80',
  'Reynisfjara Black Sand Beach': 'https://images.unsplash.com/photo-1531168556467-80aace0d0144?w=800&auto=format&fit=crop&q=80',
  'Louvre Art Museum Paris': 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800&auto=format&fit=crop&q=80',
  'French Riviera Nice Beaches': 'https://images.unsplash.com/photo-1533104816931-20fa691ff6ca?w=800&auto=format&fit=crop&q=80',
  'Lofoten Islands Scenic Tour': 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&auto=format&fit=crop&q=80',
  'Tromso Northern Lights Hunting': 'https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=800&auto=format&fit=crop&q=80',
  'Oslo Fjords & Museum Peninsula': 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&auto=format&fit=crop&q=80',
  'Geirangerfjord Cruising': 'https://images.unsplash.com/photo-1520769669658-f07657f5a307?w=800&auto=format&fit=crop&q=80',

  // ─── Châu Mỹ ──────────────────────────────────────────
  'New York Times Square Neon': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800&auto=format&fit=crop&q=80',
  'Grand Canyon South Rim': 'https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=800&auto=format&fit=crop&q=80',
  'Galapagos Islands Wildlife cruise': 'https://images.unsplash.com/photo-1547036980-1095cf077e20?w=800&auto=format&fit=crop&q=80',
  'Easter Island Rapa Nui Moai': 'https://images.unsplash.com/photo-1600078686889-8c2d32f9a008?w=800&auto=format&fit=crop&q=80',
  'Torres del Paine National Park': 'https://images.unsplash.com/photo-1531794590132-5c04be1a0972?w=800&auto=format&fit=crop&q=80',
  'Coffee Triangle Plantation Tour': 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=800&auto=format&fit=crop&q=80',
  'Panama Canal Miraflores Locks': 'https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?w=800&auto=format&fit=crop&q=80',
  'Old Havana Classic Cars': 'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=800&auto=format&fit=crop&q=80',
  'Varadero Beach Resorts': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
  'Negril Cliffs & Seven Mile Beach': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80',
  'Blue Mountains Coffee Tour': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&auto=format&fit=crop&q=80',
  'Crystal Beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',

  // ─── Châu Phi ─────────────────────────────────────────
  'Serengeti National Park Safari': 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&auto=format&fit=crop&q=80',
  'Mount Kilimanjaro Summit Climb': 'https://images.unsplash.com/photo-1621414050946-1b936a78cf55?w=800&auto=format&fit=crop&q=80',
  'Morondava Avenue of Baobabs': 'https://images.unsplash.com/photo-1504945005722-33670dcaf685?w=800&auto=format&fit=crop&q=80',
  'Chamarel Coloured Earth Dunes': 'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=800&auto=format&fit=crop&q=80',

  // ─── Châu Đại Dương ───────────────────────────────────
  'Yasawa Islands Coral Reefs': 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
  'To Sua Ocean Trench Swim': 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
  'La Digue Anse Source Beach': 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',

  // ─── UAE ──────────────────────────────────────────────
  'United Arab Emirates Summit Peak Adventure': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&auto=format&fit=crop&q=80',
  'United Arab Emirates Hidden Valley Trail': 'https://images.unsplash.com/photo-1547483238-2cbf881a559f?w=800&auto=format&fit=crop&q=80',
  'United Arab Emirates Ancient Royal Palace': 'https://images.unsplash.com/photo-1518638150341-db700683457a?w=800&auto=format&fit=crop&q=80',
  'United Arab Emirates Coastal Horizon Beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
  
  // ─── Curated additions for missing destinations ──────
  'Angkor Wat Heritage Park': 'https://images.unsplash.com/photo-1569700679541-2e70dcc19800?w=800&auto=format&fit=crop&q=80',
  'Algarve Cliffs & Caves': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
  'Almaty Charyn Canyon': 'https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=800&auto=format&fit=crop&q=80',
  'Antwerp Diamond District': 'https://images.unsplash.com/photo-1559113202-c916b8e44373?w=800&auto=format&fit=crop&q=80',
  'Arenal Volcano Hot Springs': 'https://images.unsplash.com/photo-1519611103964-90f61a44f486?w=800&auto=format&fit=crop&q=80',
  'Astana Bayterek Tower': 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&auto=format&fit=crop&q=80',
  'Bagan Hot Air Balloon Valley': 'https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?w=800&auto=format&fit=crop&q=80',
  'Bergen Bryggen Wharf': 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&auto=format&fit=crop&q=80',
  'Boracay Island White Beach': 'https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=800&auto=format&fit=crop&q=80',
  'Budapest Parliament on Danube': 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&auto=format&fit=crop&q=80',
  'Cartagena Spanish Walled City': 'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=800&auto=format&fit=crop&q=80',
  'Tromso Northern Lights Hunting': 'https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=800&auto=format&fit=crop&q=80',
  'Tromsø Northern Lights Hunting': 'https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=800&auto=format&fit=crop&q=80',
};

// ── COUNTRY-SPECIFIC IMAGES: Ảnh đại diện theo quốc gia ──────────────────────
// Dùng cho các địa điểm generic (Hidden Valley Trail, Ancient Royal Palace, v.v.)
// Mỗi quốc gia có 4 ảnh ứng với 4 loại du lịch chính
const COUNTRY_IMAGES = {
  'Singapore': {
    nature: 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1565967511849-76a60a516170?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&auto=format&fit=crop&q=80',
  },
  'Switzerland': {
    nature: 'https://images.unsplash.com/photo-1527668752968-14dc70a27c95?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1502784444187-359ac186c5bb?w=800&auto=format&fit=crop&q=80',
  },
  'Maldives': {
    nature: 'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=800&auto=format&fit=crop&q=80',
  },
  'India': {
    nature: 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1564507592937-25994a9015b2?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?w=800&auto=format&fit=crop&q=80',
  },
  'South Korea': {
    nature: 'https://images.unsplash.com/photo-1579169326371-e7c429da59e0?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1538485399081-7191377e8241?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1579169326371-e7c429da59e0?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=800&auto=format&fit=crop&q=80',
  },
  'Turkey': {
    nature: 'https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1519112232436-9923c6ba3d26?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?w=800&auto=format&fit=crop&q=80',
  },
  'United Kingdom': {
    nature: 'https://images.unsplash.com/photo-1506377585622-bedcbb027afc?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1506377585622-bedcbb027afc?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1506377585622-bedcbb027afc?w=800&auto=format&fit=crop&q=80',
  },
  'Japan': {
    nature: 'https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?w=800&auto=format&fit=crop&q=80',
  },
  'Indonesia': {
    nature: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1501179691627-eeaa65ea017c?w=800&auto=format&fit=crop&q=80',
  },
  'Thailand': {
    nature: 'https://images.unsplash.com/photo-1504214208698-ea1916a2195a?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1504214208698-ea1916a2195a?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1504214208698-ea1916a2195a?w=800&auto=format&fit=crop&q=80',
  },
  'China': {
    nature: 'https://images.unsplash.com/photo-1513415277900-a62401e19be4?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1513415277900-a62401e19be4?w=800&auto=format&fit=crop&q=80',
  },
  'France': {
    nature: 'https://images.unsplash.com/photo-1533104816931-20fa691ff6ca?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1533104816931-20fa691ff6ca?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=80',
  },
  'Italy': {
    nature: 'https://images.unsplash.com/photo-1534445867742-43195f401b6c?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1515859005217-8a1f08870f59?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1534445867742-43195f401b6c?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&auto=format&fit=crop&q=80',
  },
  'Spain': {
    nature: 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=800&auto=format&fit=crop&q=80',
  },
  'Australia': {
    nature: 'https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1506953823976-52e1fdc0149a?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=800&auto=format&fit=crop&q=80',
  },
  'New Zealand': {
    nature: 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800&auto=format&fit=crop&q=80',
  },
  'Egypt': {
    nature: 'https://images.unsplash.com/photo-1539768942893-daf53e736b68?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1539768942893-daf53e736b68?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1539768942893-daf53e736b68?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1539768942893-daf53e736b68?w=800&auto=format&fit=crop&q=80',
  },
  'Kenya': {
    nature: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&auto=format&fit=crop&q=80',
  },
  'South Africa': {
    nature: 'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1484318571209-661cf29a69c3?w=800&auto=format&fit=crop&q=80',
  },
  'Tanzania': {
    nature: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1621414050946-1b936a78cf55?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1621414050946-1b936a78cf55?w=800&auto=format&fit=crop&q=80',
  },
  'Peru': {
    nature: 'https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800&auto=format&fit=crop&q=80',
  },
  'Argentina': {
    nature: 'https://images.unsplash.com/photo-1518022525094-e099d3adb126?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1518022525094-e099d3adb126?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1518022525094-e099d3adb126?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1518022525094-e099d3adb126?w=800&auto=format&fit=crop&q=80',
  },
  'Colombia': {
    nature: 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=800&auto=format&fit=crop&q=80',
  },
  'Chile': {
    nature: 'https://images.unsplash.com/photo-1531794590132-5c04be1a0972?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1531794590132-5c04be1a0972?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1531794590132-5c04be1a0972?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1531794590132-5c04be1a0972?w=800&auto=format&fit=crop&q=80',
  },
  'Ecuador': {
    nature: 'https://images.unsplash.com/photo-1547036980-1095cf077e20?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1547036980-1095cf077e20?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1547036980-1095cf077e20?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1547036980-1095cf077e20?w=800&auto=format&fit=crop&q=80',
  },
  'Costa Rica': {
    nature: 'https://images.unsplash.com/photo-1519611103964-90f61a44f486?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1519611103964-90f61a44f486?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1519611103964-90f61a44f486?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1519611103964-90f61a44f486?w=800&auto=format&fit=crop&q=80',
  },
  'Panama': {
    nature: 'https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?w=800&auto=format&fit=crop&q=80',
  },
  'Cuba': {
    nature: 'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=800&auto=format&fit=crop&q=80',
  },
  'Jamaica': {
    nature: 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&auto=format&fit=crop&q=80',
  },
  'Fiji': {
    nature: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
  },
  'Samoa': {
    nature: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
  },
  'Madagascar': {
    nature: 'https://images.unsplash.com/photo-1504945005722-33670dcaf685?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1504945005722-33670dcaf685?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1504945005722-33670dcaf685?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1504945005722-33670dcaf685?w=800&auto=format&fit=crop&q=80',
  },
  'Seychelles': {
    nature: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
  },
  'Mauritius': {
    nature: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
  },
  'Malaysia': {
    nature: 'https://images.unsplash.com/photo-1596803244618-8dbee61a3e52?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1596803244618-8dbee61a3e52?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1580655653885-65763b2597d0?w=800&auto=format&fit=crop&q=80',
  },
  'Philippines': {
    nature: 'https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1570789210967-2cac24ee872d?w=800&auto=format&fit=crop&q=80',
  },
  'Cambodia': {
    nature: 'https://images.unsplash.com/photo-1569700679541-2e70dcc19800?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1569700679541-2e70dcc19800?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1559628233-100c798642d4?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1569700679541-2e70dcc19800?w=800&auto=format&fit=crop&q=80',
  },
  'Laos': {
    nature: 'https://images.unsplash.com/photo-1558431382-27e303142255?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1583417267826-aebc4d1542e1?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1558431382-27e303142255?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1549421263-6e398d5c4146?w=800&auto=format&fit=crop&q=80',
  },
  'Myanmar': {
    nature: 'https://images.unsplash.com/photo-1540611025311-01df3cef54b5?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1538076761142-07c47c1d1b5a?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1540611025311-01df3cef54b5?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1540611025311-01df3cef54b5?w=800&auto=format&fit=crop&q=80',
  },
  'Sri Lanka': {
    nature: 'https://images.unsplash.com/photo-1580191947416-62d35a55e71d?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1586613835341-e0ce4f711e2a?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1580191947416-62d35a55e71d?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1580191947416-62d35a55e71d?w=800&auto=format&fit=crop&q=80',
  },
  'Nepal': {
    nature: 'https://images.unsplash.com/photo-1516302752625-fcc3c50ae61f?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1558799401-1dcdef79d949?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1516302752625-fcc3c50ae61f?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1516302752625-fcc3c50ae61f?w=800&auto=format&fit=crop&q=80',
  },
  'Taiwan': {
    nature: 'https://images.unsplash.com/photo-1588997718457-6278d0756dca?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1470004914212-05527e49370b?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1588997718457-6278d0756dca?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1588997718457-6278d0756dca?w=800&auto=format&fit=crop&q=80',
  },
  'Mongolia': {
    nature: 'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=800&auto=format&fit=crop&q=80',
  },
  'Kazakhstan': {
    nature: 'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1517823382935-51bfcb0ec6bc?w=800&auto=format&fit=crop&q=80',
  },
  'Netherlands': {
    nature: 'https://images.unsplash.com/photo-1512470876337-d64b2680e3a3?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1550931454-41e17df20e06?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1512470876337-d64b2680e3a3?w=800&auto=format&fit=crop&q=80',
  },
  'Belgium': {
    nature: 'https://images.unsplash.com/photo-1491557345352-5929e343eb89?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1559113202-c916b8e44373?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1491557345352-5929e343eb89?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1491557345352-5929e343eb89?w=800&auto=format&fit=crop&q=80',
  },
  'Austria': {
    nature: 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&auto=format&fit=crop&q=80',
  },
  'Czech Republic': {
    nature: 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&auto=format&fit=crop&q=80',
  },
  'Poland': {
    nature: 'https://images.unsplash.com/photo-1477346611705-65d1883cee1e?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1562154926-190a02f1a96c?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1477346611705-65d1883cee1e?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1477346611705-65d1883cee1e?w=800&auto=format&fit=crop&q=80',
  },
  'Hungary': {
    nature: 'https://images.unsplash.com/photo-1551867633-194f125bddfa?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1551867633-194f125bddfa?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1551867633-194f125bddfa?w=800&auto=format&fit=crop&q=80',
  },
  'Croatia': {
    nature: 'https://images.unsplash.com/photo-1555990538-1d3c0e30e55c?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1555990538-1d3c0e30e55c?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1555990538-1d3c0e30e55c?w=800&auto=format&fit=crop&q=80',
  },
  'Portugal': {
    nature: 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1585208798174-6cedd86e019a?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=800&auto=format&fit=crop&q=80',
  },
  'Ireland': {
    nature: 'https://images.unsplash.com/photo-1590098563414-82b19b37cc05?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1549918864-48ac978761a4?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1548571364-cee53ee7ea7a?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1590098563414-82b19b37cc05?w=800&auto=format&fit=crop&q=80',
  },
  'Sweden': {
    nature: 'https://images.unsplash.com/photo-1509356843151-3e7d96241e11?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1509356843151-3e7d96241e11?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1509356843151-3e7d96241e11?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1509356843151-3e7d96241e11?w=800&auto=format&fit=crop&q=80',
  },
  'Denmark': {
    nature: 'https://images.unsplash.com/photo-1513622470522-26c3c8a854bc?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1513622470522-26c3c8a854bc?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1513622470522-26c3c8a854bc?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1513622470522-26c3c8a854bc?w=800&auto=format&fit=crop&q=80',
  },
  'Finland': {
    nature: 'https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1548777123-e216912df7d8?w=800&auto=format&fit=crop&q=80',
  },
  'Iceland': {
    nature: 'https://images.unsplash.com/photo-1476610182048-b716b8515aaa?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1515224526905-51c7d77c7057?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1531168556467-80aace0d0144?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1476610182048-b716b8515aaa?w=800&auto=format&fit=crop&q=80',
  },
  'Norway': {
    nature: 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1520769669658-f07657f5a307?w=800&auto=format&fit=crop&q=80',
  },
  'Greece': {
    nature: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&auto=format&fit=crop&q=80',
    cultural: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&auto=format&fit=crop&q=80',
    beach: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&auto=format&fit=crop&q=80',
    mountain: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&auto=format&fit=crop&q=80',
  },
  'Vietnam': {
    nature: [
      'https://images.unsplash.com/photo-1528127269322-539801943592?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1500627869374-13cd993b1115?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=800&auto=format&fit=crop&q=80'
    ],
    cultural: [
      'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1569700679541-2e70dcc19800?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1583417267826-aebc4d1542e1?w=800&auto=format&fit=crop&q=80'
    ],
    beach: [
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=800&auto=format&fit=crop&q=80'
    ],
    mountain: [
      'https://images.unsplash.com/photo-1508873696983-2dfd5898f08b?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=800&auto=format&fit=crop&q=80'
    ],
    urban: [
      'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800&auto=format&fit=crop&q=80'
    ]
  },
};

// ── Simple hash function to consistently map a name to an index ───────────────
const getStringHash = (str) => {
  let hash = 0;
  if (!str) return hash;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0;
  }
  return Math.abs(hash);
};

// ── Resolve category key from type and name ──────────────────────────────────
const resolveCategoryKey = (type, name = '') => {
  const n = name ? name.toLowerCase() : '';

  // 1. High priority keyword-based override only for waterfalls (which have custom nature image requirements)
  if (n.includes('falls') || n.includes('waterfall')) return 'waterfall';

  // 2. Fallback to category type
  if (!type) return 'default';
  const t = type.toLowerCase();
  if (t.includes('beach') || t.includes('biển') || t.includes('đảo')) return 'beach';
  if (t.includes('mountain') || t.includes('núi') || t.includes('phượt')) return 'mountain';
  if (t.includes('cultur') || t.includes('văn hóa') || t.includes('lịch sử') || t.includes('temple') || t.includes('religious') || t.includes('tôn giáo')) return 'cultural';
  if (t.includes('nature') || t.includes('thiên nhiên') || t.includes('rừng') || t.includes('khám phá')) return 'nature';
  if (t.includes('adventur') || t.includes('mạo hiểm') || t.includes('phiêu lưu')) return 'adventure';
  if (t.includes('urban') || t.includes('đô thị') || t.includes('thành phố') || t.includes('sầm uất') || t.includes('city') || t.includes('plaza')) return 'urban';
  return 'default';
};

/**
 * Kiểm tra xem tên địa điểm có phải là tên generic không.
 * Các tên generic: "Country + Hidden Valley Trail", "Country + Ancient Royal Palace", etc.
 * Hoặc: "Crystal Beach", "Golden Temple", "Serene Valley", etc.
 */
const isGenericName = (name) => {
  const genericSuffixes = [
    'Hidden Valley Trail', 'Ancient Royal Palace', 'Coastal Horizon Beach', 'Summit Peak Adventure',
    'Hidden Valley', 'Hidden Beach', 'Hidden Canyon', 'Hidden Falls', 'Hidden Forest',
    'Hidden Pagoda', 'Hidden Park', 'Hidden Plaza', 'Hidden Ruins', 'Hidden Temple',
  ];
  const genericPrefixes = ['Crystal', 'Golden', 'Grand', 'Lush', 'Mystic', 'Sacred', 'Serene'];

  for (const suffix of genericSuffixes) {
    if (name.endsWith(suffix)) return true;
  }

  const parts = name.split(' ');
  if (parts.length === 2 && genericPrefixes.includes(parts[0])) return true;

  return false;
};

/**
 * Trích xuất tên quốc gia từ tên địa điểm generic.
 * Ví dụ: "Chile Hidden Valley Trail" → "Chile"
 */
const extractCountryFromGenericName = (name) => {
  const genericSuffixes = [
    'Hidden Valley Trail', 'Ancient Royal Palace', 'Coastal Horizon Beach', 'Summit Peak Adventure',
  ];
  for (const suffix of genericSuffixes) {
    if (name.endsWith(suffix)) {
      return name.replace(suffix, '').trim();
    }
  }
  return '';
};

/**
 * Lấy URL hình ảnh cho một địa điểm du lịch.
 *
 * Thứ tự ưu tiên:
 *   1. EXACT_DESTINATION_IMAGES (hình đã kiểm duyệt thủ công)
 *   2. COUNTRY_IMAGES (hình theo quốc gia + loại, cho tên generic)
 *   3. IMAGES_BY_TYPE fallback (hình chung theo loại)
 *
 * @param {string} name - Tên địa điểm
 * @param {string} type - Loại du lịch (Beach, Mountain, Cultural, Urban, Nature)
 * @param {string} country - Quốc gia (tùy chọn)
 * @returns {string} URL hình ảnh
 */
export const getDestinationImage = (name, type, country) => {
  if (!name) return IMAGES_BY_TYPE.default[0];

  const trimmedName = name.trim();

  // 1. Ưu tiên cao nhất: hình đã kiểm duyệt thủ công
  if (EXACT_DESTINATION_IMAGES[trimmedName]) {
    return EXACT_DESTINATION_IMAGES[trimmedName];
  }

  const categoryKey = resolveCategoryKey(type, trimmedName);

  // 2. Nếu là tên generic, thử dùng ảnh theo quốc gia + loại (chỉ khi có mảng ảnh đa dạng)
  if (isGenericName(trimmedName) && categoryKey !== 'waterfall') {
    const countryName = country || extractCountryFromGenericName(trimmedName);
    const countryImages = COUNTRY_IMAGES[countryName];
    if (countryImages) {
      const imgType = (categoryKey === 'adventure' || categoryKey === 'default')
        ? 'nature'
        : categoryKey;
      const val = countryImages[imgType] || countryImages.nature;
      // Chỉ dùng COUNTRY_IMAGES khi có mảng (đảm bảo đa dạng), bỏ qua single string
      if (Array.isArray(val) && val.length > 1) {
        const hash = getStringHash(trimmedName);
        const index = hash % val.length;
        return val[index];
      }
    }
  }

  // 3. Fallback: sinh hình riêng biệt cho mỗi địa điểm dựa trên tên + quốc gia + loại
  const hash = getStringHash(trimmedName + (country || '') + categoryKey);
  const images = IMAGES_BY_TYPE[categoryKey] || IMAGES_BY_TYPE.default;
  const index = hash % images.length;
  return images[index];
};

/**
 * Lấy hình ảnh fallback (dùng IMAGES_BY_TYPE) khi URL chính bị lỗi.
 * Gọi hàm này trong onError của <img> tag.
 */
export const getFallbackImage = (name, type) => {
  const categoryKey = resolveCategoryKey(type, name);
  const images = IMAGES_BY_TYPE[categoryKey] || IMAGES_BY_TYPE.default;
  const hash = getStringHash((name || '') + categoryKey);
  const index = hash % images.length;
  return images[index];
};
