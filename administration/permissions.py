# Auto increments exponentially
class Counter:
    def __init__(self):
        self.__counter = -1

    @property
    def count(self):
        self.__counter += 1
        return 2 ** self.__counter


# This is to we dont need to write 2**$index
counter = Counter()
# permissions for office
OFFICE_VIEW = counter.count
OFFICE_CREATE = counter.count
OFFICE_EDIT = counter.count
OFFICE_DELETE = counter.count

# permissions for dealers
DEALER_VIEW = counter.count
DEALER_CREATE = counter.count
DEALER_EDIT = counter.count
DEALER_DELETE = counter.count

# permissions for deals
DEAL_VIEW = counter.count
DEAL_CREATE = counter.count
DEAL_EDIT = counter.count
DEAL_DELETE = counter.count

# permissions for deal areas (need to add routes for add/edit/delete)
AREA_VIEW = counter.count
AREA_CREATE = counter.count
AREA_EDIT = counter.count
AREA_DELETE = counter.count

# permissions for deal types (need to add routes for add/edit/delete)
PROPERTY_VIEW = counter.count
PROPERTY_CREATE = counter.count
PROPERTY_EDIT = counter.count
PROPERTY_DELETE = counter.count

# permissions for deal types (need to add routes for add/edit/delete)
OUTLOOK_VIEW = counter.count
OUTLOOK_CREATE = counter.count
OUTLOOK_EDIT = counter.count
OUTLOOK_DELETE = counter.count

# permissions for roles (need to add routes for add/edit/delete)
ROLE_VIEW = counter.count
ROLE_CREATE = counter.count
ROLE_EDIT = counter.count
ROLE_DELETE = counter.count

# permissions for subscription offer (need to add routes for add/edit/delete)
OFFER_VIEW = counter.count
OFFER_CREATE = counter.count
OFFER_EDIT = counter.count
OFFER_DELETE = counter.count

PURCHASE_VIEW = counter.count

GIVEAWAY_CREATE = counter.count

TRANSACTION_VIEW = counter.count

DIRECTPAY_CREATE = counter.count

# KWTSMSBALANCE_VIEW = counter.count
# KWTSMSBALANCE_CREATE = counter.count
# KWTSMSBALANCE_EDIT = counter.count
# KWTSMSBALANCE_DELETE = counter.count

# KWTSMSSENDERID_VIEW = counter.count
# KWTSMSSENDERID_CREATE = counter.count
# KWTSMSSENDERID_EDIT = counter.count
# KWTSMSSENDERID_DELETE = counter.count

# KWTSMSDLR_VIEW = counter.count
# KWTSMSDLR_CREATE = counter.count
# KWTSMSDLR_EDIT = counter.count
# KWTSMSDLR_DELETE = counter.count

# KWTSMSSEND_VIEW = counter.count
# KWTSMSSEND_CREATE = counter.count
# KWTSMSSEND_EDIT = counter.count
# KWTSMSSEND_DELETE = counter.count

# MESSAGE_VIEW = counter.count
# MESSAGE_CREATE = counter.count
# MESSAGE_EDIT = counter.count
# MESSAGE_DELETE = counter.count
# Auto generate dictionarty of all permissions
permissions_dict = {
    k: v for k, v in locals().items() if k.find("_") != -1 and k.find("__") == -1
}
