const appendAttachLink = () => {
    let btn = `
    <div class="attach-links-section pattern1">
      <button class="btn btn-primary solid-primary-btn mb-3" >Attach video link</button>
      <ul class="list-group"></ul>
    </div>`;

    $('h6:contains("Media")').parent().append(btn);

    // if media attachment already exist
    displayAttachedLinks();

    $('.attach-links-section button').click(function () {
        let links = prompt(
            'Please enter links from Youtube or Vimeo. Separate multiple links with commas.'
        );
        if (links) {
            if (!frappe.web_form.doc.media) {
                frappe.web_form.doc.media = [];
            }

            let media = frappe.web_form.doc.media;
            let linkArr = links.split(',');

            linkArr.forEach((link) => {
                // check if link exist
                let idxExist = media.findIndex((mediaObj) => {
                    return mediaObj['attachment'] === link;
                });

                if (checkMedialUrl(link) && idxExist < 0) {
                    media.push({
                        attachment: link,
                        type: 'link'
                    });
                } else if (idxExist > -1) {
                    alert('Provided link already exists.');
                } else {
                    alert('Please enter links from Youtube or Vimeo only.');
                }
            });

            displayAttachedLinks();
        }
    });
};

const checkMedialUrl = function (url) {
    const regex = /(youtube|youtu|vimeo)\.(com|be)\/((watch\?v=([-\w]+))|(video\/([-\w]+))|(projects\/([-\w]+)\/([-\w]+))|([-\w]+))/;

    if (url.match(regex)) {
        return true;
    } else {
        return false;
    }
};

const displayAttachedLinks = () => {
    if (!frappe.web_form.doc.media) {
        return;
    }
    let media = frappe.web_form.doc.media;

    let linkArr = [];
    $('.attach-links-section ul').empty();
    if (media && media.length) {
        linkArr = media.filter((mediaObj) => mediaObj['type'] === 'link');
    }

    for (const [index, link] of linkArr.entries()) {
        let unorderedList = `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        ${link['attachment']}
        <button type="button" class="close" id="removeBtn-${
          index + 1
        }" data-attachment="${link.attachment}" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
      </li>`;

        $('.attach-links-section ul').append(unorderedList);
        let btnId = `#removeBtn-${index + 1}`;

        // remove button event listener
        $(btnId).click(function () {
            let linkText = $(this).attr('data-attachment');

            if (media) {
                let foundIndex = media.findIndex((linkObj) => {
                    return linkObj['attachment'] === linkText;
                });

                if (foundIndex > -1) {
                    media.splice(foundIndex, 1);
                    displayAttachedLinks();
                }
            }
        });
    }
};