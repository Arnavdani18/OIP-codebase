const add_help_icon = () => {
    $('.help-box').each(function (){
      const helpBox = $(this);
      if (helpBox.context.textContent) {
        const helpIcon = $(`<i class="octicon octicon-question text-muted actions"></i>`);
        $(helpIcon).click(() => {
          helpBox.toggleClass('hidden');
        })
        helpBox
        .removeClass('small')
        .addClass('hidden')
        .parent()
        .prev()
        .append(helpIcon)
        .append(helpBox);
      }
    })
  }