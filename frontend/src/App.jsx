import {Routes, Route} from "react-router-dom"
import {SignedIn, SignedOut, RedirectToSignIn} from "@clerk/clerk-react";
import Layout from "./components/Layout.jsx"
import HomePage from "./pages/HomePage.jsx";
import SignInPage from "./pages/SignInPage.jsx";
import SignUpPage from "./pages/SignUp.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import PricingPage from "./pages/PricingPage.jsx";

function ProtectedRoute({children}) {
    return <>
        <SignedIn>{children}</SignedIn>
        <SignedOut>
            <RedirectToSignIn />
        </SignedOut>
    </>
}

function App() {
    return <Routes>
        <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path={"sign-in/*"} element={<SignInPage />}/>
            <Route path={"sign-up/*"} element={<SignUpPage />}/>
            <Route path={"pricing"} element={<PricingPage />}/>
            <Route
                path={"dashboard"}
                element={
                <ProtectedRoute>
                    <DashboardPage />
                </ProtectedRoute>
                }
            />
        </Route>
    </Routes>
}

export default App