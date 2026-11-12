import { Component, Input } from '@angular/core';
import { CampApplicationClient } from './camp-application-client';
@Component({ selector: 'apply-for-camp', template: '<gds-button>Apply</gds-button>' })
export class ApplyForCampView {
  @Input() client!: CampApplicationClient;
}
