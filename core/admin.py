from django.contrib import admin

from core.models import Bank, PayoutAccount, Product, ProductImage, ContractQuestion, Agreement, DisputeReason, Dispute, \
    DisputeImage, ProtectionFee, User, FAQs


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined', 'last_login',)
    list_filter = ('is_staff', 'is_active', 'date_joined', 'last_login',)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_filter = ('name',)


@admin.register(PayoutAccount)
class PayoutAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank', 'account_number', 'account_name', 'balance', 'user', 'created_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'amount', 'fee', 'user', 'receiver', 'created_at')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image', 'created_at')


@admin.register(ContractQuestion)
class ContractQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'additions', 'created_at')


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('id', 'receiver', 'product', 'question', 'answer', 'created_at')


@admin.register(DisputeReason)
class DisputeReasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reason', 'created_at')


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'reason', 'description', 'created_at')


@admin.register(DisputeImage)
class DisputeImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'dispute', 'photo', 'created_at')


@admin.register(ProtectionFee)
class ProtectionFeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'fee', 'is_percent', 'created_at')


@admin.register(FAQs)
class FAQsAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer', 'created_at')