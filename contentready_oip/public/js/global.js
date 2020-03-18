frappe.ready(async () => {
  // Simple sleep(ms) function from https://stackoverflow.com/a/48882182
  const sleep = m => new Promise(r => setTimeout(r, m));
  await sleep(200);

  $('main').removeClass('container my-5');
  $('nav.navbar').addClass('navbar-section');
  $('ul.navbar-nav:even').addClass('nav-left-list');
  $('ul.navbar-nav:odd').addClass('nav-right-list');
  $('ul.navbar-nav:even .nav-link.active').addClass('tab-focus');


  let search = $('a[href="/search"]');
  search.addClass('d-md-flex align-items-md-center');
  search.html('<span class="d-block d-lg-none">Search</span>');
  search.prepend(
    '<img src="/files/Search.svg" class="mr-4" height="20" width="20" />'
  );

  $('li.nav-item.dropdown.logged-in a').addClass(
    'd-flex align-items-center mr-4'
  );
  $('li.nav-item.dropdown.logged-in a span.full-name').attr('hidden', true);
  $('div.standard-image').css({
    height: '3rem',
    width: '3rem',
    'text-align': 'center'
  });

  $('ul.dropdown-menu').addClass('dropdown-section');
  // menu button
  $('button.navbar-toggler').addClass('py-2');

  // changing My Account to Edit Profile
  const dropdownList = $('a[href="/me"]');
  dropdownList.attr('href', '/update-profile');
  dropdownList.text('Profile');

  if (frappe.session.user === 'Guest') {
    $('a:contains("Add a Problem / Solution")').hide();

  } else {
    $('a:contains("Add a Problem / Solution")').addClass('add-problem-btn');
    $('a:contains("Add a Problem / Solution")')
      .next()
      .addClass('dropdown-menu-right');

    // fix moving of nav while clicking menu icon
    $('nav div.container').addClass('nav-container');

    // chnge the list order
    $('.nav-right-list')
      .find('li:eq(0)')
      .insertAfter('.nav-right-list li:eq(2)');

    // insert add problem/solution and search logo
    let addProblem = $('a[href="/add-problem?new=1"]');
    let addSolution = $('a[href="/add-solution?new=1"]');

    addProblem.prepend(
      '<img src="/files/problem_dark.svg" height="22" width="30" />'
    );

    addSolution.prepend(
      '<img src="/files/solution_dark.svg" height="22" width="30" />'
    );

    addProblem.addClass('py-2');
    addSolution.addClass('py-2');
  }
});
