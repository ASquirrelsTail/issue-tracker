function selectToChips(selectID, chipsID) {
    // Replaces a select multi input with a series of toggleable chips inside the targeted element.
    // Select input should be sr-only, chips div should be aria-hidden to preserve accessibility.
    $('#' + selectID + ' option').each(function() {
        let option = $(this);
        let name = option.text();
        let value = option.attr('value');
        let selected = option.prop('selected') ? 'selected' : null;
        $('#' + chipsID).append(`<div class="chip ${selected}" data-value="${value}">${name}</div>`);
    });

    $('#' + chipsID + ' .chip').on('click', function() {
        let chip = $(this)
        let option = $('#' + selectID + ' option[value="' + chip.data('value') + '"');
        option.prop('selected', !option.prop('selected'));
        chip.toggleClass('selected');
    });
}

$(function() {
    // Refocus on the username input when the login modal is shown
    $('#loginModal').on('shown.bs.modal', function() {
        $(this).find('#id_username')[0].focus();
    });
});
