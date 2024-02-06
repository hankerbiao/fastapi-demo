import json
import os
import requests


class AutoGrafana:
    def __init__(self, cfg_, grafana_path):
        self.cfg = cfg_  # 加载配置文件
        self.grafana_url = self.cfg.get('url') + '/'  # 获取API地址
        self.grafana_path = grafana_path

    @property
    def headers(self):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.cfg.get('Authorization', "").replace("Bearer", "")
        }
        return headers

    def delete_grafana_dashboard_by_uid(self, uid=None, dashboard_name=None):
        """Delete Grafana dashboard by UID."""
        delete_results = []
        search_url = 'search'
        search_response = requests.get(self.grafana_url + search_url, headers=self.headers)
        dashboards = search_response.json()

        # 检查是否有错误信息
        if isinstance(dashboards, dict) and 'message' in dashboards:
            error_message = dashboards.get('message')
            if error_message in ['Invalid Basic Auth Header', 'Not found', 'invalid API key']:
                raise Exception(error_message)
                # return False, str(dashboards)

        # 获取要被删除的看板UID
        dashboard_uids = [dashboard["uid"] for dashboard in dashboards if dashboard["uid"] == uid] if uid else [
            dashboard["uid"] for dashboard in dashboards]

        if not dashboard_uids:
            delete_results.append('No dashboard found.\n')
            return True, delete_results

        # 删除看板
        for dashboard_uid in dashboard_uids:
            delete_response = requests.delete(f"{self.grafana_url}dashboards/uid/{dashboard_uid}", headers=self.headers)
            if delete_response.status_code == 200:
                delete_results.append(f"{dashboard_name}(旧), UID: {dashboard_uid} 删除成功！.\n")

        return True, delete_results

    def delete_all_data_sources(self):
        """Delete all Grafana data sources."""
        result_messages = []
        data_sources_url = f'{self.grafana_url}datasources'
        data_sources_response = requests.get(data_sources_url, headers=self.headers)
        if data_sources_response.status_code != 200:
            raise Exception(data_sources_response.content.decode("utf8"))
            # return False, str(data_sources_response.json())
        data_sources = json.loads(data_sources_response.content)

        # Delete all data sources
        for datasource in data_sources:
            delete_response = requests.delete(f'{self.grafana_url}datasources/{datasource["id"]}', headers=self.headers)
            if delete_response.status_code == 200:
                result_messages.append(f'数据源 {datasource["name"]} 删除成功!.\n')
            else:
                result_messages.append(
                    f'Failed to delete data source {datasource["name"]}: {delete_response.content}\n')
                raise Exception(delete_response.content)

        return True, result_messages

    def import_data_sources(self):
        """Import Grafana data sources."""
        import_results = []
        delete_response, msg = self.delete_all_data_sources()
        import_results = import_results + msg
        if not delete_response:
            return import_results
        data_sources_path = os.path.join(self.grafana_path, 'AutoGrafana/data_sources.json')
        with open(data_sources_path, 'r') as f:
            data_sources = json.load(f)

        for data_source in data_sources:
            data_source_type = data_source.get('type')
            if data_source_type:
                data_source['url'] = self.cfg.get(data_source_type)
            import_response = requests.post(self.grafana_url + 'datasources', headers=self.headers,
                                            json=data_source)
            if import_response.status_code == 200:
                print(f'Data source {data_source["name"]} imported successfully')
                import_results.append(f'Data source {data_source["name"]} imported successfully.\n')
            else:
                print(f'Failed to import data source {data_source["name"]}')
                import_results.append(f'Failed to import data source {data_source["name"]}\n')
                import_results.append(import_response.json())
                raise Exception(import_response.json())

        return import_results

    def create_dashboard(self):
        """Create Grafana dashboard."""
        response = []
        dashboards_path = os.path.join(self.grafana_path, 'AutoGrafana/dashboards')
        create_url = self.grafana_url + 'dashboards/db'  # Construct URL
        dashboard_files = os.listdir(dashboards_path)  # Get all files in the directory

        for dashboard_file in dashboard_files:  # Loop through all files
            dashboard_path = os.path.join(dashboards_path, dashboard_file)
            if not dashboard_path.endswith('.json'):  # Check if the file is a JSON file
                continue
            with open(dashboard_path, 'r', encoding='utf8') as file:  # Open the file
                dashboard_data = json.loads(file.read())  # Read the file content and convert JSON data to dictionary
                uid = dashboard_data['dashboard']['uid']
                dashboard_name = os.path.split(dashboard_path)[1]
                delete_dashboard_res, delete_dashboard_info = self.delete_grafana_dashboard_by_uid(uid=uid,
                                                                                                   dashboard_name=dashboard_name)
                response = response + delete_dashboard_info
                if not delete_dashboard_res:
                    return response
                create_response = requests.post(create_url, data=json.dumps(dashboard_data),
                                                headers=self.headers)  # Send POST request
                # Check if the request is successful based on the status code
                if create_response.status_code == 200:
                    print(f"{dashboard_file} created successfully.")
                    response.append(f"{dashboard_file} imported successfully.\n")
                else:
                    print(dashboard_path)
                    print(create_response.json())
                    print(f"Request failed with status code {create_response.status_code}.")
                    response.append(f"Request failed with status code {create_response.status_code}.\n")

        return response
