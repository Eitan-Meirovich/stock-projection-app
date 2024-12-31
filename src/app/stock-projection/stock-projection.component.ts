import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stock-projection',
  templateUrl: './stock-projection.component.html',
  styleUrls: ['./stock-projection.component.css'],
  standalone: true,
  imports: [CommonModule]
})
export class StockProjectionComponent implements OnInit {
  superFamilies: string[] = [];
  families: string[] = [];
  productCodes: string[] = [];
  tableData: any[] = [];
  private allData: any[] = [];
  resultsVisible = false;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get('assets/consolidado_datos.csv', { responseType: 'text' }).subscribe(
      (data) => {
        this.processCSVData(data as string);
      },
      (error) => {
        console.error('Error al cargar el archivo CSV:', error);
      }
    );
  }

  filterData(field: string, value: string): void {
    this.tableData = this.allData.filter(item => item[field] === value);
  }

  private processCSVData(csvData: string): void {
    const rows = csvData.split('\n');
    const headers = rows[0].split(',').map(header => header.trim());

    this.allData = rows.slice(1).filter(row => row.trim().length > 0).map(row => {
      const values = row.split(',');
      return headers.reduce((acc, header, index) => {
        acc[header] = values[index]?.trim() || '';
        return acc;
      }, {} as any);
    });

    this.superFamilies = [...new Set(this.allData.map(item => item['Super Familia'] || ''))];
    this.families = [...new Set(this.allData.map(item => item['Familia'] || ''))];
    this.productCodes = [...new Set(this.allData.map(item => item['Codigo Producto'] || ''))];
  }

  runProjection(): void {
    this.resultsVisible = true;
  }
}