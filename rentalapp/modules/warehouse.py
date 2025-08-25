from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from rentalapp.forms import WarehouseItemForm
from rentalapp.models import WarehouseItem, WarehouseLog


class WarehouseViews:

    @staticmethod
    def warehouse_manager_view(request):
        items = WarehouseItem.objects.all()
        return render(request, 'rentalapp/warehouse/warehouse_manager.html', {'items': items})

    @staticmethod
    def warehouse_add_item_view(request):
        if request.method == 'POST':
            name = request.POST.get('name')
            quantity = request.POST.get('quantity')
            date_state = request.POST.get('date_state')
            comment = request.POST.get('comment', '')

            if name and quantity and date_state:
                new_item = WarehouseItem.objects.create(
                    name=name,
                    quantity=int(quantity),
                    date_state=date_state,
                    comment=comment
                )
                messages.success(request, f"Dodano przedmiot: {name}")

                WarehouseLog.objects.create(
                    item=new_item,
                    user=request.user,
                    quantity_taken=int(quantity),
                    message=f"{request.user.username} dodał {quantity} szt. przedmiotu '{new_item.name}'."
                )

                return redirect('rentalapp:warehouse_manager')
            else:
                messages.error(request, "Wypełnij wszystkie wymagane pola.")

        return render(request, 'rentalapp/warehouse/warehouse_add_item.html')

    @staticmethod
    def warehouse_delete_item_view(request, pk):
        item = get_object_or_404(WarehouseItem, pk=pk)
        item.delete()
        messages.warning(request, f"Usunięto przedmiot: {item.name}")
        return redirect('rentalapp:warehouse_manager')

    @staticmethod
    def warehouse_delete_selected_view(request):
        if request.method == 'POST':
            items_ids = request.POST.getlist('selected_items')
            WarehouseItem.objects.filter(pk__in=items_ids).delete()
            messages.warning(request, f"Usunięto zaznaczone przedmioty.")
        return redirect('rentalapp:warehouse_manager')

    @staticmethod
    def warehouse_undo_view(request):
        messages.info(request, "Cofnięto ostatnią operację (funkcjonalność do zaimplementowania).")
        return redirect('rentalapp:warehouse_manager')

    @staticmethod
    def warehouse_edit_item_view(request, pk):
        item = get_object_or_404(WarehouseItem, pk=pk)
        old_quantity = item.quantity
        if request.method == "POST":
            form = WarehouseItemForm(request.POST, instance=item)
            if form.is_valid():
                updated_item = form.save()
                new_quantity = updated_item.quantity

                if new_quantity != old_quantity:
                    quantity_diff = new_quantity - old_quantity
                    abs_diff = abs(quantity_diff)

                    if quantity_diff > 0:
                        message_text = f"{request.user.username} dodał {abs_diff} szt. do przedmiotu '{updated_item.name}'."
                    else:
                        message_text = f"{request.user.username} zabrał {abs_diff} szt. z przedmiotu '{updated_item.name}'."

                    WarehouseLog.objects.create(
                        item=updated_item,
                        user=request.user,
                        quantity_taken=quantity_diff,
                        message=message_text
                    )

                messages.success(request, f"Ilość przedmiotu '{updated_item.name}' została zaktualizowana.")
                return redirect('rentalapp:warehouse_manager')
            else:
                messages.error(request, "Formularz zawiera błędy.")
        else:
            form = WarehouseItemForm(instance=item)

        return render(request, "rentalapp/warehouse/warehouse_edit_item.html", {"form": form, "item": item})

    @staticmethod
    def warehouse_logs_view(request):
        logs = WarehouseLog.objects.all().order_by('-timestamp')
        return render(request, 'rentalapp/warehouse/warehouse_logs.html', {'logs': logs})
