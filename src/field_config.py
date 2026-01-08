"""
Field Configuration Module
Centralized field definitions and keyword mappings for column mapping feature.
"""

# Standard field categories and their display names (bilingual)
FIELD_CATEGORIES = {
    "ignore": {"en": "Ignore", "zh": "忽略"},
    "id": {"en": "ID/Identifier", "zh": "ID/标识"},
    "customer": {"en": "Customer Info", "zh": "客户信息"},
    "datetime": {"en": "Date/Time", "zh": "时间日期"},
    "product": {"en": "Product Info", "zh": "产品信息"},
    "numeric": {"en": "Numeric/Financial", "zh": "数值财务"},
    "status": {"en": "Status/Category", "zh": "状态类别"},
    "text": {"en": "Text/Notes", "zh": "文本备注"}
}

# Standard fields with their categories, labels, and detection keywords
STANDARD_FIELDS = {
    # ========== ID/标识 ==========
    "SaleID": {
        "category": "id",
        "label_en": "Sale ID",
        "label_zh": "订单ID",
        "keywords": [
            "id", "客户id", "用户编号", "订单号", "序列号", "记录号", "唯一标识",
            "customer_id", "user_id", "order_id", "serial", "record_id", "编号"
        ]
    },
    
    # ========== 客户信息 ==========
    "CustomerName": {
        "category": "customer",
        "label_en": "Customer Name",
        "label_zh": "客户姓名",
        "keywords": [
            "姓名", "用户名", "联系人", "name", "username", "contact", "客户名", "客户姓名"
        ]
    },
    "Phone": {
        "category": "customer",
        "label_en": "Phone",
        "label_zh": "电话",
        "keywords": [
            "手机号", "电话", "phone", "mobile", "tel", "联系电话", "手机"
        ]
    },
    "Email": {
        "category": "customer",
        "label_en": "Email",
        "label_zh": "邮箱",
        "keywords": [
            "邮箱", "email", "mail", "电子邮件", "e-mail"
        ]
    },
    "Address": {
        "category": "customer",
        "label_en": "Address",
        "label_zh": "地址",
        "keywords": [
            "地址", "address", "location", "详细地址", "收货地址"
        ]
    },
    "Province": {
        "category": "customer",
        "label_en": "Province",
        "label_zh": "省份",
        "keywords": [
            "省份", "province", "state", "省"
        ]
    },
    "City": {
        "category": "customer",
        "label_en": "City",
        "label_zh": "城市",
        "keywords": [
            "城市", "city", "市"
        ]
    },
    "Department": {
        "category": "customer",
        "label_en": "Department",
        "label_zh": "部门",
        "keywords": [
            "部门", "department", "dept", "所属部门"
        ]
    },
    
    # ========== 时间日期 ==========
    "OrderDate": {
        "category": "datetime",
        "label_en": "Order Date",
        "label_zh": "订单日期",
        "keywords": [
            "日期", "时间", "创建时间", "更新日期", "开始日期", "结束日期",
            "date", "time", "created_at", "updated_at", "start_date", "end_date",
            "注册日期", "订单日期", "下单时间", "购买日期"
        ]
    },
    
    # ========== 产品信息 ==========
    "ProductName": {
        "category": "product",
        "label_en": "Product Name",
        "label_zh": "产品名称",
        "keywords": [
            "商品名称", "产品名", "product", "item", "goods", "产品", "商品"
        ]
    },
    "SKU": {
        "category": "product",
        "label_en": "SKU",
        "label_zh": "商品编码",
        "keywords": [
            "sku", "商品编码", "product_code", "货号", "商品sku"
        ]
    },
    "ProductCategory": {
        "category": "product",
        "label_en": "Product Category",
        "label_zh": "产品类别",
        "keywords": [
            "产品类别", "商品分类", "category", "产品分类", "商品类别"
        ]
    },
    "Model": {
        "category": "product",
        "label_en": "Model",
        "label_zh": "型号",
        "keywords": [
            "型号", "model", "specification", "规格", "机型"
        ]
    },
    
    # ========== 数值财务 ==========
    "TotalPrice": {
        "category": "numeric",
        "label_en": "Total Price",
        "label_zh": "总价",
        "keywords": [
            "金额", "价格", "总计", "amount", "price", "total", "money",
            "薪资", "薪水", "salary", "总金额", "总价", "消费金额"
        ]
    },
    "UnitPrice": {
        "category": "numeric",
        "label_en": "Unit Price",
        "label_zh": "单价",
        "keywords": [
            "单价", "unit_price", "单位价格"
        ]
    },
    "Quantity": {
        "category": "numeric",
        "label_en": "Quantity",
        "label_zh": "数量",
        "keywords": [
            "数量", "quantity", "qty", "count", "购买数量"
        ]
    },
    "Revenue": {
        "category": "numeric",
        "label_en": "Revenue",
        "label_zh": "收入",
        "keywords": [
            "收入", "revenue", "income", "营收"
        ]
    },
    "Cost": {
        "category": "numeric",
        "label_en": "Cost",
        "label_zh": "成本",
        "keywords": [
            "成本", "cost", "expense", "费用"
        ]
    },
    "Age": {
        "category": "numeric",
        "label_en": "Age",
        "label_zh": "年龄",
        "keywords": [
            "年龄", "age", "岁"
        ]
    },
    "Rating": {
        "category": "numeric",
        "label_en": "Rating",
        "label_zh": "评分",
        "keywords": [
            "评分", "rating", "score", "评价", "打分"
        ]
    },
    
    # ========== 状态类别 ==========
    "Status": {
        "category": "status",
        "label_en": "Status",
        "label_zh": "状态",
        "keywords": [
            "状态", "status", "state", "订单状态"
        ]
    },
    "Type": {
        "category": "status",
        "label_en": "Type",
        "label_zh": "类型",
        "keywords": [
            "类型", "type", "kind"
        ]
    },
    "Category": {
        "category": "status",
        "label_en": "Category",
        "label_zh": "分类",
        "keywords": [
            "分类", "类别", "category"
        ]
    },
    "Level": {
        "category": "status",
        "label_en": "Level",
        "label_zh": "等级",
        "keywords": [
            "等级", "level", "grade", "rank", "级别"
        ]
    },
    "Gender": {
        "category": "status",
        "label_en": "Gender",
        "label_zh": "性别",
        "keywords": [
            "性别", "gender", "sex"
        ]
    },
    "IsValid": {
        "category": "status",
        "label_en": "Is Valid",
        "label_zh": "是否有效",
        "keywords": [
            "是否有效", "有效性", "valid", "is_valid", "active", "启用"
        ]
    },
    
    # ========== 文本备注 ==========
    "Description": {
        "category": "text",
        "label_en": "Description",
        "label_zh": "描述",
        "keywords": [
            "描述", "详情", "说明", "description", "detail", "note"
        ]
    },
    "Remarks": {
        "category": "text",
        "label_en": "Remarks",
        "label_zh": "备注",
        "keywords": [
            "备注", "注释", "remarks", "comment", "notes", "备注信息"
        ]
    }
}


def get_field_options_by_category():
    """
    Get field options organized by category for UI display.
    Returns a list of tuples: (field_key, display_label)
    """
    options = [("Ignore", "Ignore (忽略)")]
    
    # Group fields by category
    categorized = {}
    for field_key, field_info in STANDARD_FIELDS.items():
        cat = field_info["category"]
        if cat not in categorized:
            categorized[cat] = []
        display_label = f"{field_info['label_zh']} ({field_key})"
        categorized[cat].append((field_key, display_label))
    
    # Add fields in category order
    category_order = ["id", "customer", "datetime", "product", "numeric", "status", "text"]
    for cat in category_order:
        if cat in categorized:
            options.extend(categorized[cat])
    
    return options


def get_field_display_name(field_key, language="zh"):
    """
    Get display name for a field.
    
    Args:
        field_key: The standard field key (e.g., "SaleID")
        language: "zh" for Chinese, "en" for English
    
    Returns:
        Display name string
    """
    if field_key == "Ignore":
        return "忽略" if language == "zh" else "Ignore"
    
    if field_key in STANDARD_FIELDS:
        label_key = f"label_{language}"
        return STANDARD_FIELDS[field_key].get(label_key, field_key)
    
    return field_key
