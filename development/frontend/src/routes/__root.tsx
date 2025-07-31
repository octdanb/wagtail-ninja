import * as React from 'react'
import { Outlet, createRootRoute } from '@tanstack/react-router'
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {useState} from "react";

export const Route = createRootRoute({
  component: RootComponent,
})




function RootComponent() {

    const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                refetchOnWindowFocus: false,
            },
            hydrate: {
                queries: {
                    retry: false,
                },
            },
            mutations: {
                retry: false,
            },
            // dehydrate: {},
        },
    }))
    return (
        <React.Fragment>
            <QueryClientProvider client={ queryClient }>
                  <Outlet />
            </QueryClientProvider>
        </React.Fragment>
    )
}
