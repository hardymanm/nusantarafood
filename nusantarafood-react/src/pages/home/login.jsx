import {Link} from "react-router-dom";

function AuthLink({to, children}) {
    return <div className="text-lime-600">
        <Link to={to}>{children}</Link>
    </div>
}

export default function Login() {
    return <div className="h-screen flex justify-center items-center  text-lime-600">
        <div className="h-3/4">
            <div className="text-4xl md:text-2xl font-bold text-center mb-6">Login to NFO</div>
            <div className="p-6 w-80 bg-lime-200 rounded mb-3">
                <input type="text" className="w-full rounded px-3 mb-2 py-1" name="username" placeholder="Username"/>
                <input type="password" className="w-full rounded px-3 mb-2 py-1" name="password" placeholder="Password"/>
                <button className="px-4 py-2 bg-lime-500 text-white rounded w-full mt-2 mb-6">Login</button>
                <AuthLink to="forgot-password">Forgot password?</AuthLink>
                <AuthLink to="forgot-password">Create account</AuthLink>
            </div>
            <div className="text-center text-lime-500">
                <Link to="/">Back to Home</Link>
            </div>
        </div>

    </div>


}