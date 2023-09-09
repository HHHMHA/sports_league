const table = $('#games-table').DataTable({
    ajax: {
        url: gameListUrl,
        dataSrc: '',
    },
    columnDefs: [
        {
            targets: [0],
            render: function (data, type, row) {
                if (type === 'display') {
                    return `<div class="id-field" >${data}</div>`;
                }
                return data;
            },
        },
        {
            targets: [2],
            render: function (data, type, row) {
                if (type === 'display') {
                    return `<input type="number" name="home_team_score" value="${data}" />`;
                }
                return data;
            },
        },
        {
            targets: [4],
            render: function (data, type, row) {
                if (type === 'display') {
                    return `<input type="number" name="away_team_score" value="${data}" />`;
                }
                return data;
            },
        },
    ],
    columns: [
        {data: 'id'},
        {data: 'home_team'},
        {data: 'home_team_score'},
        {data: 'away_team'},
        {data: 'away_team_score'},
    ]
});

$('#update-btn').on('click', function (e) {
    e.preventDefault();
    const row = table.row('.selected');
    if (!row.any()) {
        toastr.error("Please select a row first");
        return;
    }
    const data = $('#games-table .selected input').serialize();

    const id = $('#games-table .selected .id-field').text();

    $.ajax({
        url: gameDetailUrl.replace("0", id),
        method: 'PUT',
        data: data,
        headers: {
            'X-CSRFToken': csrftoken, // Include the CSRF token in the headers
        },
        success: function (response) {
            table.ajax.reload();
        },
        error: function (xhr, textStatus, errorThrown) {
        }
    });
});

$('#add-btn').on('click', function (e) {
    e.preventDefault();

    const form = document.getElementById("add-game-form");
    if (!form.reportValidity()) {
        return;
    }

    const data = $('#add-game-form').serialize();

    $.ajax({
        url: gameListUrl,
        method: 'POST',
        data: data,
        headers: {
            'X-CSRFToken': csrftoken, // Include the CSRF token in the headers
        },
        success: function (response) {
            table.ajax.reload();
        },
        error: function (xhr, textStatus, errorThrown) {
            if (xhr.responseJSON){
                if (xhr.responseJSON.non_field_errors) {
                    toastr.error(xhr.responseJSON.non_field_errors[0]);
                    return;
                }
            }
            toastr.error("Unknown error");
        }
    });
});

table.on('click', 'tbody tr', (e) => {
    let classList = e.currentTarget.classList;

    if (classList.contains('selected')) {
        classList.remove('selected');
    } else {
        table.rows('.selected').nodes().each((row) => row.classList.remove('selected'));
        classList.add('selected');
    }
});

document.querySelector('#remove-btn').addEventListener('click', function () {
    const row = table.row('.selected');
    if (!row.any()) {
        toastr.error("Please select a row first");
        return;
    }
    const rowData = row.data();
    const id = rowData["id"];
    $.ajax({
        url: gameDetailUrl.replace("0", id),
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken, // Include the CSRF token in the headers
        },
        success: function (response) {
            // Remove the row from the DataTables table
            row.remove().draw(false);
            table.ajax.reload();
        },
        error: function (xhr, textStatus, errorThrown) {
        }
    });
});
