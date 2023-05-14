console.log('Hi');
document.addEventListener('DOMContentLoaded', function() {
    console.log('Hi');
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        selectable: true,
        select: function(info) {
            // Create a form/modal to get start and end times
            var form = document.createElement('form');
            var startInput = document.createElement('input');
            startInput.type = 'time';
            startInput.name = 'start_time';
            var endInput = document.createElement('input');
            endInput.type = 'time';
            endInput.name = 'end_time';
            var submitButton = document.createElement('button');
            submitButton.textContent = 'Submit';

            form.appendChild(startInput);
            form.appendChild(endInput);
            form.appendChild(submitButton);

            // Show the form/modal
            var modal = document.createElement('div');
            modal.classList.add('modal');
            modal.appendChild(form);
            document.body.appendChild(modal);

            // Handle form submission
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                var startTime = startInput.value;
                var endTime = endInput.value;

                // Send Pomodoro session data to Flask using AJAX request
                $.ajax({
                    type: "POST",
                    url: "/pomodoro",
                    data: {
                        start_time: startTime,
                        end_time: endTime
                    },
                    success: function(response) {
                        // Handle success response from Flask (if any)
                        console.log(response);
                    },
                    error: function(xhr, status, error) {
                        // Handle error response from Flask (if any)
                        console.log(xhr.responseText);
                    }
                });

                // Hide the modal
                modal.style.display = 'none';

                // Show a confirmation message
                alert('Pomodoro session scheduled from ' + startTime + ' to ' + endTime);
            });
        },
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        events: {
            url: '/get-events',
            method: 'GET'
        }
    });

    console.log('HI');

    calendar.render();
});