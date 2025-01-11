README
------

The meeting links are slightly hidden to avoid abuse from web scraping bots,
which is why we use the hCAPTCHA to add a small deterrent.

If just changing the meeting info/links, skip down to `Updating Meeting
Info` section.


Background
----------
The github pages are statically generated. Therefore, we can not use a
server-side reCAPTCHA method (e.g., Open MPI uses a server-side PHP
reCAPTCHA).  We use hCAPTCHA and an entirely client-side method that is
compatible with static gh-pages.  

Note, since the data is pasted in the client side, we base64 encode the
information to obfuscate the information and reduce direct browsing of
meeting info.  See notes for updating things and encoding the meeting info.

General Flow
------------

 1. User visits `/captcha` URL, and completes the challenge prompt.

 2. On success, redirected to "success" page (e.g., `success.html`) with
    the meeting information.
    - Note: We generate a simple token on captcha page (`index.html`) that
      is checked by the `success.html` page to try and avoid simple browsing
      of the full URL.  This is a weak protection to help obfuscate the
      meeting info data.
    - Note: We base64 encode the meeting content and embed the data into the
      success page where it is displayed.  This is a weak protection to help
      obfuscate the meeting info data.

 3. On failure, redirected to captcha challenge prompt.


Initial Setup
-------------

One-time setup for the basic `/captcha` directory in repository.

 1. (One-time setup) Create hCaptcha free account and generate `sitekey`
    - Note: Currently using setup under naughtont AT ornl.gov account.
    - Note: Using 'Always Challenge' and 'Easy' settings.
    - https://dashboard.hcaptcha.com/sites?page=1&archived=active

 2. Edit `index.html`, update `data-sitekey` with `sitekey` from Step 1.

 3. Commit changes to repo and the gh-pages will be updated automatically.

 4. Now ready to update meeting info (see below).


Update Meeting Info
-------------------

Assumes initial setup (above) complete and just changing meeting data.

 1. Manually format the "meeting info" with any desired HTML formatting.

 2. Encode (base64) the meeting data (e.g., `meetings.dat => meetings.dat.enc`)
    - NOTE: You can decode the meeting data to double check encode/decode
      using the same script (see: `encode.py -h`)

    ```
      ./_misc/encode.py meetings.dat > meetings.dat.enc
    ```

 3. Edit `success.html`, update `encodedData` with contents of encoded data
    string (e.g., copy/paste `meetings.dat.enc`).

 4. As needed, update any titles/headings in HTML (e.g., 2025 Meetings).

 5. Commit changes to repo and the gh-pages will be updated automatically.


Misc
----

 - The `_misc/` dir has leading underscore so Jekyll ignores it
   when posting content to the statically generated gh-pages
 - Encode script at `_misc/encode.py`
 - Example HTML formatted meeting data at `_misc/example.dat`

