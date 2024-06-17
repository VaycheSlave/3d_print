function executeCommand(command) {
            var xhr = new XMLHttpRequest();
            var form = new FormData();
            form.append("command", command);

            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        document.getElementById("status").innerHTML = "Задача выполнена успешно.";
                    } else {
                        document.getElementById("status").innerHTML = "Ошибка: " + xhr.responseText;
                    }
                }
            };

            xhr.open("POST", "/control_printer/", true);
            xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");
            xhr.send(form);

            return false;  // Чтобы предотвратить перезагрузку страницы
        }