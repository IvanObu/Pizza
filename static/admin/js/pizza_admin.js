document.addEventListener('DOMContentLoaded', function () {
    const auto = document.getElementById('id_auto_calculate');
    if (!auto) return;

    const coefFieldset = document.querySelector('fieldset.coef-fields');
    const manualBlocks = document.querySelectorAll('fieldset.manual-fields');
    const basePrice = document.getElementById('id_base_price_s');
    const baseWeight = document.getElementById('id_base_weight_s');

    const manualInputs = [
        'id_price_m', 'id_price_l', 'id_price_xl',
        'id_weight_m', 'id_weight_l', 'id_weight_xl'
    ].map(id => document.getElementById(id));

    const sizes = {
        m: { priceId: 'id_price_multiplier_m', weightId: 'id_weight_multiplier_m', label: 'M (30 см)' },
        l: { priceId: 'id_price_multiplier_l', weightId: 'id_weight_multiplier_l', label: 'L (35 см)' },
        xl: { priceId: 'id_price_multiplier_xl', weightId: 'id_weight_multiplier_xl', label: 'XL (40 см)' }
    };

    function createPreview(formRow) {
        let preview = document.createElement('div');
        preview.className = 'calc-preview';
        preview.innerHTML = `<strong>Итог:</strong> <span class="price">—</span> ₽ / <span class="weight">—</span> г`;
        formRow.appendChild(preview);
        return preview;
    }

    function recalc() {
        if (!auto.checked) return;

        const priceS = parseFloat(basePrice.value) || 0;
        const weightS = parseFloat(baseWeight.value) || 0;

        Object.values(sizes).forEach(cfg => {
            const priceInput = document.getElementById(cfg.priceId);
            const weightInput = document.getElementById(cfg.weightId);
            if (!priceInput || !weightInput) return;

            let preview = priceInput.closest('.form-row').querySelector('.calc-preview');
            if (!preview) preview = createPreview(priceInput.closest('.form-row'));

            const price = (priceS * parseFloat(priceInput.value || 0)).toFixed(0);
            const weight = (weightS * parseFloat(weightInput.value || 0)).toFixed(0);

            preview.querySelector('.price').textContent = price;
            preview.querySelector('.weight').textContent = weight;
        });
    }

    function toggleBlocks() {
        const enabled = auto.checked;

        // Показываем/скрываем блоки
        if (coefFieldset) coefFieldset.style.display = enabled ? '' : 'none';
        manualBlocks.forEach(fs => fs.style.display = enabled ? 'none' : '');

        // Если включен авторасчет — очищаем все ручные поля
        if (enabled) {
            manualInputs.forEach(input => {
                if (input) input.value = '';
            });
        }

        recalc();
    }

    auto.addEventListener('change', toggleBlocks);
    basePrice.addEventListener('input', recalc);
    baseWeight.addEventListener('input', recalc);

    document.querySelectorAll('[id^="id_price_multiplier"], [id^="id_weight_multiplier"]')
        .forEach(el => el.addEventListener('input', recalc));

    toggleBlocks(); 
});