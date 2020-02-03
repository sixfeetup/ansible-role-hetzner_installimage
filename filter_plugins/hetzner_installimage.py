from ansible_filter import form_urlencode


class FilterModule(object):

    def filters(self):
        return {
            'hetzner_installimage_form_urlencode': form_urlencode.form_urlencode
    }