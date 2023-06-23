// Scripts

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});


// Fix Button Staying in Focus
var elements = document.querySelectorAll('.btn');
for (var i = 0; i < elements.length; i++) {
  var element = elements[i];
  element.addEventListener('click', function() {
    this.blur();
  });
}

// Add Animation to Buttons
$('.reloadButton').hover(
    function(){ $(this).children().addClass('fa-spin') },
    function(){ $(this).children().removeClass('fa-spin') }
)
$('.modBtn').hover(
    function(){ $(this).children().addClass('fa-spin') },
    function(){ $(this).children().removeClass('fa-spin') }
)
$('.addBtn').hover(
    function(){ $(this).children().addClass('fa-beat') },
    function(){ $(this).children().removeClass('fa-beat') }
)

// Changing Tabs in Index
$('#tab a[data-bs-toggle="tab"]').on('show.bs.tab', function(e) {
    let target = $(e.target).data('bs-target');
    $(target)
      .addClass('active show')
      .siblings('.tab-pane.active')
      .removeClass('active show')

    let targetID = $(e.target).data('id');
    if (typeof targetID !== 'undefined') {
        const request = new XMLHttpRequest()
        request.open('POST', `/getActualTab/${targetID}`)
        request.send();
    }
})


// Create Progress Bar
$(".animated-progress span").each(function () {
    $(this).animate(
      {
        width: $(this).attr("data-progress") + "%",
      },
      1000
    );
    $(this).text($(this).attr("data-progress") + "%");
});
