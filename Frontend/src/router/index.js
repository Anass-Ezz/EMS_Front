import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    name: 'dashboard',
                    component: () => import('@/views/pages/Dashboard.vue')
                },
                {
                    path: '/unifilaire',
                    name: 'unifilaire',
                    component: () => import('@/views/pages/DiagramPage.vue')
                },
                {
                    path: '/meters',
                    name: 'meters',
                    component: () => import('@/views/pages/MetersPage.vue')
                },
                {
                    path: '/gas-meters',
                    name: 'gas-meters',
                    component: () => import('@/views/pages/GasMetersPage.vue')
                },
                {
                    path: '/fuel-meters',
                    name: 'fuel-meters',
                    component: () => import('@/views/pages/FuelMetersPage.vue')
                }, 
                {
                    path: '/pv',
                    name: 'pv',
                    component: () => import('@/views/pages/PvPage.vue')
                }, 
                {
                    path: '/reports',
                    name: 'reports',
                    component: () => import('@/views/pages/ReportsPage.vue')
                },
                {
                    path: '/settings',
                    name: 'settings',
                    component: () => import('@/views/pages/SettingsPage.vue')
                },
                {
                    path: '/support',
                    name: 'support',
                    component: () => import('@/views/pages/SupportPage.vue')
                }, 
                // {
                //     path: '/unifilaire',
                //     name: 'unifilaire',
                //     component: () => import('@/views/pages/Unifilaire.vue')
                // },
                // {
                //     path: '/consumption',
                //     name: 'consumptionPage',
                //     component: () => import('@/views/pages/ConsumptionPage.vue')
                // },
                // {
                //     path: '/pv',
                //     name: 'pvPage',
                //     component: () => import('@/views/pages/PvPage.vue')
                // },
                // {
                //     path: '/wt',
                //     name: 'wtPage',
                //     component: () => import('@/views/pages/WindTurbinePage.vue')
                // },
                // {
                //     path: '/battery',
                //     name: 'batteryPage',
                //     component: () => import('@/views/pages/BatteryPage.vue')
                // },
                // {
                //     path: '/energy',
                //     name: 'energyPage',
                //     component: () => import('@/views/pages/EnergyPage.vue')
                // },
                // {
                //     path: '/export',
                //     name: 'exportPage',
                //     component: () => import('@/views/pages/ExportPage.vue')
                // },
                // {
                //     path: '/forecasting/environment',
                //     name: 'forcastingEnvirenmentPage',
                //     component: () => import('@/views/pages/ForcastingEnvirenmentPage.vue')
                // },
                
                // {
                //     path: '/uikit/formlayout',
                //     name: 'formlayout',
                //     component: () => import('@/views/uikit/FormLayout.vue')
                // },
                // {
                //     path: '/uikit/input',
                //     name: 'input',
                //     component: () => import('@/views/uikit/InputDoc.vue')
                // },
                // {
                //     path: '/uikit/button',
                //     name: 'button',
                //     component: () => import('@/views/uikit/ButtonDoc.vue')
                // },
                // {
                //     path: '/uikit/table',
                //     name: 'table',
                //     component: () => import('@/views/uikit/TableDoc.vue')
                // },
                // {
                //     path: '/uikit/list',
                //     name: 'list',
                //     component: () => import('@/views/uikit/ListDoc.vue')
                // },
                // {
                //     path: '/uikit/tree',
                //     name: 'tree',
                //     component: () => import('@/views/uikit/TreeDoc.vue')
                // },
                // {
                //     path: '/uikit/panel',
                //     name: 'panel',
                //     component: () => import('@/views/uikit/PanelsDoc.vue')
                // },

                // {
                //     path: '/uikit/overlay',
                //     name: 'overlay',
                //     component: () => import('@/views/uikit/OverlayDoc.vue')
                // },
                // {
                //     path: '/uikit/media',
                //     name: 'media',
                //     component: () => import('@/views/uikit/MediaDoc.vue')
                // },
                // {
                //     path: '/uikit/message',
                //     name: 'message',
                //     component: () => import('@/views/uikit/MessagesDoc.vue')
                // },
                // {
                //     path: '/uikit/file',
                //     name: 'file',
                //     component: () => import('@/views/uikit/FileDoc.vue')
                // },
                // {
                //     path: '/uikit/menu',
                //     name: 'menu',
                //     component: () => import('@/views/uikit/MenuDoc.vue')
                // },
                // {
                //     path: '/uikit/charts',
                //     name: 'charts',
                //     component: () => import('@/views/uikit/ChartDoc.vue')
                // },
                // {
                //     path: '/uikit/misc',
                //     name: 'misc',
                //     component: () => import('@/views/uikit/MiscDoc.vue')
                // },
                // {
                //     path: '/uikit/timeline',
                //     name: 'timeline',
                //     component: () => import('@/views/uikit/TimelineDoc.vue')
                // },
                // {
                //     path: '/pages/empty',
                //     name: 'empty',
                //     component: () => import('@/views/pages/Empty.vue')
                // },
                // {
                //     path: '/pages/crud',
                //     name: 'crud',
                //     component: () => import('@/views/pages/Crud.vue')
                // },
                // {
                //     path: '/documentation',
                //     name: 'documentation',
                //     component: () => import('@/views/pages/Documentation.vue')
                // }
            ]
        },
        // {
        //     path: '/landing',
        //     name: 'landing',
        //     component: () => import('@/views/pages/Landing.vue')
        // },
        // {
        //     path: '/pages/notfound',
        //     name: 'notfound',
        //     component: () => import('@/views/pages/NotFound.vue')
        // },

        // {
        //     path: '/auth/login',
        //     name: 'login',
        //     component: () => import('@/views/pages/auth/Login.vue')
        // },
        {
            path: '/auth/access',
            name: 'accessDenied',
            component: () => import('@/views/auth/Access.vue')
        },
        {
            path: '/auth/error',
            name: 'error',
            component: () => import('@/views/auth/Error.vue')
        },
        {
            path: '/auth/login',
            name: 'loginPage',
            component: () => import('@/views/auth/Login.vue')
        },
    ]
});

export default router;
