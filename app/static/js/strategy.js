//async function addRule(rule) {
//    const token = localStorage.getItem("access_token");
//
//    if (!token) {
//        alert("Token not found! Please login first.");
//        return;
//    }
//
//    const response = await fetch('/api/strategy_rules', {
//        method: 'POST',
//        headers: {
//            'Content-Type': 'application/json',
//            'Authorization': `Bearer ${token}`
//        },
//        body: JSON.stringify(rule)
//    });
//
//    if (!response.ok) {
//        const text = await response.text();
//        alert("Error adding rule: " + response.status + " " + text);
//    } else {
//        alert("Rule added successfully!");
//    }
//}
