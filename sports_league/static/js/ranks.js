const table = $('#ranks-table').DataTable({
    ajax: {
        url: ranksUrl,
        dataSrc: '',
    },
    columns: [
        {data: 'rank'},
        {data: 'team'},
        {data: 'points'},
    ],
});

$('#strategy-filter').on('change', function () {
    const selectedValue = $(this).val();

    table.ajax.url(`${ranksUrl}?strategy=${selectedValue}`).load();
});
