#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\vgsclient\store.py
from collections import defaultdict
import contextlib
import logging
from vgsclient.account import Account
log = logging.getLogger(__name__)

class PurchaseInProgressError(Exception):
    pass


class PurchaseFailedError(Exception):
    pass


class Store:

    def __init__(self, vgsCrestConnection, lockImpl):
        self.vgsCrestConnection = vgsCrestConnection
        self.loadingLock = lockImpl()
        self._ResetVariables()
        self.purchaseInProgress = False
        self.account = Account(vgsCrestConnection)

    def ClearCache(self):
        self._ResetVariables()
        self.account.ClearCache()

    def _ResetVariables(self):
        self.productsById = None
        self.offersById = None
        self.offersByProductId = None
        self.offersByTagId = None
        self.categoriesById = None
        self.rootCategoriesById = None
        self.tagsById = None

    def GetAccount(self):
        return self.account

    def _PrimeSearchIndex(self):
        self.offersByProductId = {}
        self.offersByTagId = defaultdict(list)
        for product in self.GetProducts().itervalues():
            self.offersByProductId[product.id] = []

        for offer in self.GetOffers().itervalues():
            for tag in offer.categories:
                if tag in self.tagsById.keys():
                    self.offersByTagId[tag].append(offer.id)

            for productId in offer.productQuantities:
                try:
                    self.offersByProductId[productId].append(offer.id)
                except KeyError:
                    log.debug('_PrimeSearchIndex: productID %s was not found while indexing offer %s', productId, offer)

    def GetOffers(self):
        if self.offersById is None:
            with self.loadingLock:
                if self.offersById is None:
                    offers = self.vgsCrestConnection.GetOffers()
                    self.offersById = {offer.id:offer for offer in offers}
        return self.offersById

    def GetOffer(self, offerId):
        return self.GetOffers()[offerId]

    def GetProducts(self):
        if self.productsById is None:
            self.productsById = {product.id:product for product in self.vgsCrestConnection.GetProducts()}
        return self.productsById

    def BuyOffer(self, offer, qty = 1):
        if self.purchaseInProgress:
            return False
        self.purchaseInProgress = True
        try:
            return self.vgsCrestConnection.BuyOffer(offer, qty=qty)
        finally:
            self.purchaseInProgress = False

    def PurchaseOffer(self, offer, quantity = 1):
        with self._PurchaseContext():
            try:
                self.vgsCrestConnection.BuyOffer(offer, qty=quantity)
            except Exception as e:
                raise PurchaseFailedError(e)

    @contextlib.contextmanager
    def _PurchaseContext(self):
        if self.purchaseInProgress:
            raise PurchaseInProgressError()
        self.purchaseInProgress = True
        try:
            yield
        finally:
            self.purchaseInProgress = False

    def GetSales(self, salesUri = None):
        return self.vgsCrestConnection.GetSales(salesUri)

    def GetSale(self, saleUri = None):
        return self.vgsCrestConnection.GetSale(saleUri)

    def SearchOffers(self, searchString):
        searchString = searchString.lower()
        if self.tagsById is None:
            self._ProcessCategories()
        if self.offersByProductId is None:
            self._PrimeSearchIndex()
        matchedOfferIds = set()
        for offer in self.offersById.itervalues():
            if searchString in offer.name.lower():
                matchedOfferIds.add(offer.id)

        for product in self.GetProducts().itervalues():
            if searchString in product.name.lower():
                matchedOfferIds.update(self.offersByProductId[product.id])

        for tag in self.tagsById.itervalues():
            if tag.name.lower().startswith(searchString):
                matchedOfferIds.update(self.offersByTagId[tag.id])

        return [ self.offersById[offerId] for offerId in matchedOfferIds ]

    def SearchOffersByTypeIDs(self, typeIDs):
        offers = self.GetOffers()
        matchedOffers = []
        for offer in offers.itervalues():
            products = offer.productQuantities.itervalues()
            productTypeIDs = [ typeID for typeID, quantity in products ]
            if any((typeID in productTypeIDs for typeID in typeIDs)):
                matchedOffers.append(offer)

        return matchedOffers

    def _ProcessCategories(self):
        categories = self.vgsCrestConnection.GetCategories()
        self.rootCategoriesById = {}
        self.tagsById = {}
        self.categoriesById = {category.id:category for category in categories}
        for category in categories:
            if category.parentId:
                self.categoriesById[category.parentId].subcategories.add(category.id)

        for category in categories:
            if category.parentId is None:
                if len(category.subcategories) > 0:
                    self.rootCategoriesById[category.id] = category
                else:
                    self.tagsById[category.id] = category

        offers = self.GetOffers()
        subCatIdsSeenByCatId = defaultdict(set)
        for offer in offers.itervalues():
            for category in self.rootCategoriesById.itervalues():
                for subCatId in category.subcategories:
                    if subCatId in offer.categories:
                        category.tagIds.update((tagId for tagId in offer.categories if tagId in self.tagsById))
                        subCatIdsSeenByCatId[category.id].add(subCatId)

        for category in self.rootCategoriesById.itervalues():
            category.subcategories.intersection_update(subCatIdsSeenByCatId[category.id])

    def GetCategories(self):
        if not self.categoriesById:
            self._ProcessCategories()
        return self.categoriesById

    def GetRootCategoryList(self):
        if not self.rootCategoriesById:
            self._ProcessCategories()
        return self.rootCategoriesById.values()

    def GetTags(self):
        if not self.tagsById:
            self._ProcessCategories()
        return self.tagsById

    def GetTagsByCategoryId(self, categoryId):
        category = self.categoriesById.get(categoryId)
        if category.parentId is not None:
            category = self.categoriesById.get(category.parentId)
        tagsById = self.GetTags()
        return [ tagsById[tagId] for tagId in category.tagIds ]

    def GetFilteredOffers(self, categoryId, tags = set()):
        categoryIds = {categoryId}
        if categoryId in self.categoriesById:
            category = self.categoriesById[categoryId]
            categoryIds.update({subCategoryId for subCategoryId in category.subcategories})
        offers = []
        for offer in self.GetOffers().itervalues():
            if categoryIds.isdisjoint(offer.categories):
                continue
            if tags and not tags.issubset(offer.categories):
                continue
            offers.append(offer)

        return offers

    def GetTagsFromOffers(self, offers):
        tagsById = self.GetTags()
        tagIds = set()
        for offer in offers:
            for tagId in offer.categories:
                if tagId in tagsById:
                    tagIds.add(tagId)

        return {tagsById[tagId] for tagId in tagIds}
