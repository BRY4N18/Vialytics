declare namespace L {
  function map(element: string | HTMLElement, options?: any): any;
  function tileLayer(url: string, options?: any): any;
  function circleMarker(latlng: [number, number], options?: any): any;
  function popup(options?: any): any;
  function marker(latlng: [number, number], options?: any): any;
  function icon(options?: any): any;
  function divIcon(options?: any): any;
  function layerGroup(): any;
  function latLngBounds(latlngs: [number, number][]): any;
  namespace control {
    function zoom(options?: any): any;
    function attribution(options?: any): any;
  }
}
