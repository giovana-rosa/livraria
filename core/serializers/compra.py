from rest_framework.serializers import CharField, DecimalField, ModelSerializer, SerializerMethodField, CurrentUserDefault, HiddenField, ValidationError
from core.models import Compra, ItensCompra
from django.db import transaction

class ItensCompraCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade')

        def validate(self, item):
        if item['quantidade'] > item['livro'].quantidade:
            raise ValidationError('Quantidade de itens maior do que a quantidade em estoque.')
        return item

class ItensCompraSerializer(ModelSerializer):
    titulo = CharField(source='livro.titulo', read_only=True)
    editora = CharField(source='livro.editora.nome', read_only=True)
    preco = DecimalField(source='livro.preco', read_only=True, max_digits=10, decimal_places=2)
    capa = CharField(source='livro.capa.url', read_only=True)
    total = SerializerMethodField()

    def get_total(self, item):
        return item.livro.preco * item.quantidade

    class Meta:
        model = ItensCompra
        fields = ('id', 'titulo', 'editora', 'quantidade', 'preco', 'capa', 'total')


class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    itens = ItensCompraSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'status', 'total', 'itens')

class CompraCreateUpdateSerializer(ModelSerializer):
    itens = ItensCompraCreateUpdateSerializer(many=True)
    usuario = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def update(self, compra, validated_data):
        itens = validated_data.pop('itens', None)
        if itens is not None:
            compra.itens.all().delete()
            for item in itens:
                ItensCompra.objects.create(compra=compra, **item)
        return super().update(compra, validated_data)

class ItensCompraListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'livro')
        depth = 1

class CompraListSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    itens = ItensCompraListSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

class ItensCompraListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'livro')
        depth = 1
