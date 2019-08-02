import jsonpickle


class JsonHelper:
    @staticmethod
    def object_as_json_to_file(filepath: str, object_to_store):
        if jsonpickle.load_backend('simplejson'):
            jsonpickle.set_preferred_backend('simplejson')
            jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        else:
            print('Couldn\'t load simplejson')
        with open(filepath, 'w') as outfile:
            json_output = jsonpickle.encode(object_to_store, unpicklable=False)
            outfile.write(json_output)

    @staticmethod
    def read_stats_from_workloads(filepath: str) -> int:
        if jsonpickle.load_backend('simplejson'):
            jsonpickle.set_preferred_backend('simplejson')
            jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        else:
            print('Couldn\'t load simplejson')
        with open('workloads.json', 'r') as outfile:
            contents = outfile.read()
            json_input = jsonpickle.decode(contents)
            return json_input[1]
