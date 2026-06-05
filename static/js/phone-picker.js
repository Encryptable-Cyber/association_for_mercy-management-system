/**
 * Association for Mercy — Phone Country Code Picker
 * Auto-updates the country code selector based on the selected country of residence.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Country code mapping (abbreviated; full map in Python)
    const COUNTRY_CODES = {
        'Cameroon': '+237', 'Nigeria': '+234', 'Chad': '+235',
        'Gabon': '+241', 'Congo': '+242', 'DR Congo': '+243',
        'Ghana': '+233', 'Ivory Coast': '+225', 'Senegal': '+221',
        'Mali': '+223', 'Burkina Faso': '+226', 'Benin': '+229',
        'Togo': '+228', 'Niger': '+227', 'Guinea': '+224',
        'Morocco': '+212', 'Algeria': '+213', 'Tunisia': '+216',
        'Egypt': '+20', 'Sudan': '+249', 'South Sudan': '+211',
        'Ethiopia': '+251', 'Kenya': '+254', 'Uganda': '+256',
        'Tanzania': '+255', 'Rwanda': '+250', 'Burundi': '+257',
        'South Africa': '+27', 'Zimbabwe': '+263', 'Zambia': '+260',
        'France': '+33', 'Belgium': '+32', 'Switzerland': '+41',
        'Germany': '+49', 'United Kingdom': '+44', 'Italy': '+39',
        'Spain': '+34', 'Portugal': '+351', 'Netherlands': '+31',
        'Sweden': '+46', 'Norway': '+47', 'Denmark': '+45',
        'Ireland': '+353', 'Poland': '+48', 'Turkey': '+90',
        'United States': '+1', 'Canada': '+1', 'Mexico': '+52',
        'Brazil': '+55', 'Argentina': '+54', 'Colombia': '+57',
        'China': '+86', 'India': '+91', 'Japan': '+81',
        'South Korea': '+82', 'Philippines': '+63', 'Vietnam': '+84',
        'Thailand': '+66', 'Indonesia': '+62', 'Malaysia': '+60',
        'Pakistan': '+92', 'Bangladesh': '+880',
        'Saudi Arabia': '+966', 'United Arab Emirates': '+971',
        'Qatar': '+974', 'Lebanon': '+961',
        'Australia': '+61', 'New Zealand': '+64',
    };

    // Find country selects and phone inputs
    const countrySelects = document.querySelectorAll('.country-select');
    const phoneFields = document.querySelectorAll('[data-phone-field]');

    if (phoneFields.length > 0) {
        phoneFields.forEach(function (phoneField) {
            const wrapper = document.createElement('div');
            wrapper.className = 'phone-input-group';

            const codeSelect = document.createElement('select');
            codeSelect.className = 'form-select country-code-select';
            codeSelect.innerHTML = '<option value="">Code</option>';
            populateCountryCodes(codeSelect, COUNTRY_CODES);

            // Move phone input into the wrapper
            phoneField.parentNode.insertBefore(wrapper, phoneField);
            wrapper.appendChild(codeSelect);
            wrapper.appendChild(phoneField);

            // When country of residence changes, update the code
            countrySelects.forEach(function (cs) {
                cs.addEventListener('change', function () {
                    const countryName = cs.value;
                    if (COUNTRY_CODES[countryName]) {
                        codeSelect.value = COUNTRY_CODES[countryName];
                    }
                });
            });

            // When user picks a code manually, store it for form submission
            codeSelect.addEventListener('change', function () {
                phoneField.setAttribute('data-country-code', codeSelect.value);
            });
        });
    }
});

function populateCountryCodes(selectEl, codeMap) {
    const seen = new Set();
    const entries = Object.entries(codeMap).sort((a, b) => a[1].localeCompare(b[1]));
    entries.forEach(function ([country, code]) {
        if (!seen.has(code)) {
            seen.add(code);
            const option = document.createElement('option');
            option.value = code;
            option.textContent = code;
            selectEl.appendChild(option);
        }
    });
}
