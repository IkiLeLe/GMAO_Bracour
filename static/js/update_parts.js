// update_part_options.js

function updateEquipementOptions() {
    var lineField = document.querySelector('#id_line');
    var equipementField = document.querySelector('#id_equipement');

    if (lineField && equipementField) {
        var lineValue = lineField.value;
        fetch(`/maintenance_plan/equipement/${lineValue}/`)
            .then(response => response.json())
            .then(data => {
                equipementField.innerHTML = "";
                data.forEach(option => {
                    var optionElement = new Option(option.text, option.value);
                    equipementField.appendChild(optionElement);
                });

                // Déclencher manuellement l'événement 'change' sur le champ 'equipement'
                var changeEvent = new Event('change');
                equipementField.dispatchEvent(changeEvent);
            })
            .catch(error => console.error('Error fetching filtered equipements:', error));
    } else {
        console.error('Line or Equipement field not found');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    updateEquipementOptions();
    document.querySelector('#id_line').addEventListener('change', updateEquipementOptions);
});

function updatePartOptions() {
    var equipementField = document.querySelector('#id_equipement');

    if (equipementField) {
        var equipementValue = equipementField.value;
        var partField = document.querySelector('#id_part');

        fetch(`/maintenance_plan/part/${equipementValue}/`)
            .then(response => response.json())
            .then(data => {
                partField.innerHTML = "";
                data.forEach(option => {
                    var optionElement = new Option(option.text, option.value);
                    partField.appendChild(optionElement);
                });

                // Récupérer l'URL de la vue depuis les données renvoyées
                var url = data.find(item => item.url)?.url;
                console.log('URL:', url);
            })
            .catch(error => console.error('Error fetching filtered parts:', error));
    } else {
        console.error('Equipement field not found');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    updatePartOptions();
    document.querySelector('#id_equipement').addEventListener('change', updatePartOptions);
});
